import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import func, inspect, text
from sqlalchemy.orm import Session
from ..config import get_settings
from ..database import Base, engine, get_db
from ..models import (
    AIGenerationRecord,
    Chapter,
    Character,
    KnowledgeItem,
    Novel,
    Outline,
    PromptTemplate,
    SubmissionRecord,
    User,
    WorldSetting,
)
from ..schemas.common import (
    AIRecordOut,
    AIRequest,
    ChapterIn,
    ChapterOut,
    CharacterIn,
    CharacterOut,
    KnowledgeItemIn,
    KnowledgeItemOut,
    NovelIn,
    NovelOut,
    OutlineIn,
    OutlineOut,
    PromptTemplateIn,
    PromptTemplateOut,
    SubmissionIn,
    SubmissionOut,
    TokenOut,
    UserCreate,
    UserLogin,
    WorldSettingIn,
    WorldSettingOut,
)
from ..services.ai_service import AIService
from ..services.export_service import ExportService
from ..services.memory_service import build_generation_context, chapter_memory
from ..services.prompt_service import get_prompt_template, seed_default_prompt_templates
from ..services.quality_service import evaluate_chapter_result
from ..utils.security import create_access_token, hash_password, verify_password
from ..utils.text import count_cn_words
from .deps import get_current_user


router = APIRouter(prefix="/api")
settings = get_settings()
ai_service = AIService()
export_service = ExportService(str(Path(__file__).resolve().parents[2] / "exports"))


def save_ai_record(
    db: Session,
    user_id: int,
    novel_id: int | None,
    generation_type: str,
    input_data: dict,
    output_data: dict,
    quality: dict | None = None,
    retry_count: int = 0,
    metrics: dict | None = None,
):
    quality = quality or {}
    metrics = metrics or getattr(ai_service, "last_metrics", {}) or {}
    record = AIGenerationRecord(
        user_id=user_id,
        novel_id=novel_id,
        generation_type=generation_type,
        input_text=json.dumps(input_data, ensure_ascii=False),
        output_text=json.dumps(output_data, ensure_ascii=False),
        quality_score=quality.get("score", 0) or 0,
        quality_report=quality.get("report", "") or "",
        retry_count=retry_count,
        ai_duration_ms=metrics.get("duration_ms", 0) or 0,
        prompt_tokens=metrics.get("prompt_tokens", 0) or 0,
        completion_tokens=metrics.get("completion_tokens", 0) or 0,
        total_tokens=metrics.get("total_tokens", 0) or 0,
        ai_success=1 if metrics.get("success", True) else 0,
        ai_error=metrics.get("error", "") or "",
    )
    db.add(record)
    db.commit()


def refresh_chapter_memory(db: Session, novel: Novel, chapter: Chapter):
    template = get_prompt_template(db, "summarize", novel.genre)
    memory = ai_service.summarize_chapter(novel, chapter, template)
    if not memory.get("summary"):
        memory = chapter_memory(chapter)
    chapter.summary = memory.get("summary", "") or ""
    chapter.memory_keywords = memory.get("memory_keywords", "") or ""


def get_novel_owned(db: Session, novel_id: int, user_id: int) -> Novel:
    novel = db.query(Novel).filter(Novel.id == novel_id, Novel.user_id == user_id).first()
    if not novel:
        raise HTTPException(status_code=404, detail="小说项目不存在")
    return novel


def get_chapter_owned(db: Session, chapter_id: int, novel_id: int) -> Chapter:
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id, Chapter.novel_id == novel_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    return chapter


@router.get("/health")
def health():
    return {"message": "ok"}


@router.post("/auth/register", response_model=TokenOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.username == payload.username).first()
    if exists:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=payload.username,
        pen_name=payload.pen_name or payload.username,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.username)
    return {
        "access_token": token,
        "user": {"id": user.id, "username": user.username, "pen_name": user.pen_name},
    }


@router.post("/auth/login", response_model=TokenOut)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    token = create_access_token(user.username)
    return {
        "access_token": token,
        "user": {"id": user.id, "username": user.username, "pen_name": user.pen_name},
    }


@router.post("/auth/token", response_model=TokenOut, tags=["认证"])
def login_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误", headers={"WWW-Authenticate": "Bearer"})
    token = create_access_token(user.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "pen_name": user.pen_name},
    }


@router.get("/auth/me")
def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "pen_name": current_user.pen_name}


@router.get("/dashboard")
def dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    novels = db.query(Novel).filter(Novel.user_id == current_user.id).all()
    novel_ids = [item.id for item in novels]
    chapters = db.query(Chapter).filter(Chapter.novel_id.in_(novel_ids)).all() if novel_ids else []
    completed = sum(1 for item in chapters if item.status == "已润色")
    waiting = sum(1 for item in chapters if item.status == "待上传")
    uploaded = sum(1 for item in chapters if item.status == "已上传")
    recent_novels = sorted(novels, key=lambda item: item.updated_at, reverse=True)[:5]
    recent_chapters = sorted(chapters, key=lambda item: item.updated_at, reverse=True)[:6]
    today = datetime.now()
    daily_words = defaultdict(int)
    for i in range(6, -1, -1):
        day = (today - timedelta(days=i)).date().isoformat()
        daily_words[day] = 0
    for chapter in chapters:
        key = chapter.updated_at.date().isoformat()
        if key in daily_words:
            daily_words[key] += chapter.word_count
    return {
        "overview": {
            "novel_count": len(novels),
            "chapter_count": len(chapters),
            "completed_chapter_count": completed,
            "pending_upload_count": waiting,
            "uploaded_count": uploaded,
        },
        "recent_novels": [NovelOut.model_validate(item).model_dump() for item in recent_novels],
        "recent_chapters": [ChapterOut.model_validate(item).model_dump() for item in recent_chapters],
        "daily_words": [{"date": key, "words": value} for key, value in daily_words.items()],
    }


@router.get("/novels", response_model=list[NovelOut])
def list_novels(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Novel).filter(Novel.user_id == current_user.id).order_by(Novel.updated_at.desc()).all()


@router.post("/novels", response_model=NovelOut)
def create_novel(payload: NovelIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    novel = Novel(user_id=current_user.id, **payload.model_dump())
    db.add(novel)
    db.commit()
    db.refresh(novel)
    return novel


@router.get("/novels/{novel_id}", response_model=NovelOut)
def get_novel(novel_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_novel_owned(db, novel_id, current_user.id)


@router.put("/novels/{novel_id}", response_model=NovelOut)
def update_novel(novel_id: int, payload: NovelIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    novel = get_novel_owned(db, novel_id, current_user.id)
    for key, value in payload.model_dump().items():
        setattr(novel, key, value)
    db.commit()
    db.refresh(novel)
    return novel


@router.delete("/novels/{novel_id}")
def delete_novel(novel_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    novel = get_novel_owned(db, novel_id, current_user.id)
    db.delete(novel)
    db.commit()
    return {"message": "已删除"}


@router.post("/ai/idea")
def generate_idea(payload: AIRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = ai_service.idea(payload.model_dump())
    save_ai_record(db, current_user.id, payload.novel_id, "创意生成", payload.model_dump(), result)
    return result


@router.post("/ai/characters")
def generate_characters(payload: AIRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    novel = get_novel_owned(db, payload.novel_id, current_user.id)
    result = ai_service.characters(novel, payload.role_type)
    save_ai_record(db, current_user.id, novel.id, "人物设定", payload.model_dump(), {"characters": result})
    return {"characters": result}


@router.get("/novels/{novel_id}/characters", response_model=list[CharacterOut])
def list_characters(novel_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_novel_owned(db, novel_id, current_user.id)
    return db.query(Character).filter(Character.novel_id == novel_id).order_by(Character.created_at.asc()).all()


@router.post("/novels/{novel_id}/characters", response_model=CharacterOut)
def create_character(novel_id: int, payload: CharacterIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_novel_owned(db, novel_id, current_user.id)
    character = Character(novel_id=novel_id, **payload.model_dump())
    db.add(character)
    db.commit()
    db.refresh(character)
    return character


@router.put("/characters/{character_id}", response_model=CharacterOut)
def update_character(character_id: int, payload: CharacterIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    character = db.query(Character).join(Novel).filter(Character.id == character_id, Novel.user_id == current_user.id).first()
    if not character:
        raise HTTPException(status_code=404, detail="人物不存在")
    for key, value in payload.model_dump().items():
        setattr(character, key, value)
    db.commit()
    db.refresh(character)
    return character


@router.delete("/characters/{character_id}")
def delete_character(character_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    character = db.query(Character).join(Novel).filter(Character.id == character_id, Novel.user_id == current_user.id).first()
    if not character:
        raise HTTPException(status_code=404, detail="人物不存在")
    db.delete(character)
    db.commit()
    return {"message": "已删除"}


@router.post("/ai/world")
def generate_world(payload: AIRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    novel = get_novel_owned(db, payload.novel_id, current_user.id)
    result = ai_service.world(novel)
    save_ai_record(db, current_user.id, novel.id, "世界观", payload.model_dump(), result)
    return result


@router.get("/novels/{novel_id}/world-settings", response_model=list[WorldSettingOut])
def list_world_settings(novel_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_novel_owned(db, novel_id, current_user.id)
    return db.query(WorldSetting).filter(WorldSetting.novel_id == novel_id).order_by(WorldSetting.created_at.desc()).all()


@router.post("/novels/{novel_id}/world-settings", response_model=WorldSettingOut)
def create_world_setting(novel_id: int, payload: WorldSettingIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_novel_owned(db, novel_id, current_user.id)
    item = WorldSetting(novel_id=novel_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/world-settings/{setting_id}", response_model=WorldSettingOut)
def update_world_setting(setting_id: int, payload: WorldSettingIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(WorldSetting).join(Novel).filter(WorldSetting.id == setting_id, Novel.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="世界观设定不存在")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/world-settings/{setting_id}")
def delete_world_setting(setting_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(WorldSetting).join(Novel).filter(WorldSetting.id == setting_id, Novel.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="世界观设定不存在")
    db.delete(item)
    db.commit()
    return {"message": "已删除"}


@router.post("/ai/outlines")
def generate_outlines(payload: AIRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    novel = get_novel_owned(db, payload.novel_id, current_user.id)
    result = ai_service.outlines(novel, payload.outline_count)
    save_ai_record(db, current_user.id, novel.id, "大纲", payload.model_dump(), result)
    return result


@router.get("/novels/{novel_id}/outlines", response_model=list[OutlineOut])
def list_outlines(novel_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_novel_owned(db, novel_id, current_user.id)
    return db.query(Outline).filter(Outline.novel_id == novel_id).order_by(Outline.chapter_number.asc()).all()


@router.post("/novels/{novel_id}/outlines", response_model=OutlineOut)
def create_outline(novel_id: int, payload: OutlineIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_novel_owned(db, novel_id, current_user.id)
    item = Outline(novel_id=novel_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/novels/{novel_id}/outlines/batch")
def batch_create_outlines(novel_id: int, payload: list[OutlineIn], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_novel_owned(db, novel_id, current_user.id)
    items = [Outline(novel_id=novel_id, **item.model_dump()) for item in payload]
    db.add_all(items)
    db.commit()
    return {"message": "已批量保存", "count": len(items)}


@router.put("/outlines/{outline_id}", response_model=OutlineOut)
def update_outline(outline_id: int, payload: OutlineIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Outline).join(Novel).filter(Outline.id == outline_id, Novel.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="大纲不存在")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/outlines/{outline_id}")
def delete_outline(outline_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Outline).join(Novel).filter(Outline.id == outline_id, Novel.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="大纲不存在")
    db.delete(item)
    db.commit()
    return {"message": "已删除"}


@router.get("/prompt-templates", response_model=list[PromptTemplateOut])
def list_prompt_templates(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(PromptTemplate).order_by(PromptTemplate.task_type.asc(), PromptTemplate.genre.asc()).all()


@router.post("/prompt-templates", response_model=PromptTemplateOut)
def create_prompt_template(payload: PromptTemplateIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = PromptTemplate(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/prompt-templates/{template_id}", response_model=PromptTemplateOut)
def update_prompt_template(template_id: int, payload: PromptTemplateIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Prompt 模板不存在")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.get("/novels/{novel_id}/knowledge-items", response_model=list[KnowledgeItemOut])
def list_knowledge_items(novel_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_novel_owned(db, novel_id, current_user.id)
    return (
        db.query(KnowledgeItem)
        .filter(KnowledgeItem.user_id == current_user.id, KnowledgeItem.novel_id == novel_id)
        .order_by(KnowledgeItem.updated_at.desc())
        .all()
    )


@router.post("/novels/{novel_id}/knowledge-items", response_model=KnowledgeItemOut)
def create_knowledge_item(novel_id: int, payload: KnowledgeItemIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_novel_owned(db, novel_id, current_user.id)
    data = payload.model_dump()
    data["novel_id"] = novel_id
    item = KnowledgeItem(user_id=current_user.id, **data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/knowledge-items/{item_id}", response_model=KnowledgeItemOut)
def update_knowledge_item(item_id: int, payload: KnowledgeItemIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id, KnowledgeItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="素材不存在")
    data = payload.model_dump()
    if data.get("novel_id"):
        get_novel_owned(db, data["novel_id"], current_user.id)
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/knowledge-items/{item_id}")
def delete_knowledge_item(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id, KnowledgeItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="素材不存在")
    db.delete(item)
    db.commit()
    return {"message": "已删除"}


@router.post("/ai/chapter")
def generate_chapter(payload: AIRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    novel = get_novel_owned(db, payload.novel_id, current_user.id)
    outline = None
    if payload.outline_id:
        outline = db.query(Outline).filter(Outline.id == payload.outline_id, Outline.novel_id == novel.id).first()
    context = build_generation_context(db, novel, current_user.id, outline, payload.instruction)
    template = get_prompt_template(db, "chapter", novel.genre)
    result = ai_service.chapter_with_context(novel, outline, context, payload.word_count, payload.writing_style, template)
    quality = evaluate_chapter_result(result, payload.word_count)
    retry_count = 0
    if not quality["passed"]:
        retry_count = 1
        result = ai_service.chapter_with_context(
            novel,
            outline,
            context,
            payload.word_count,
            payload.writing_style,
            template,
            quality["report"],
        )
        quality = evaluate_chapter_result(result, payload.word_count)
    output = {**result, "_quality": quality, "_retry_count": retry_count}
    save_ai_record(db, current_user.id, novel.id, "章节正文", {"request": payload.model_dump(), "context": context}, output, quality, retry_count)
    return result


@router.get("/novels/{novel_id}/chapters", response_model=list[ChapterOut])
def list_chapters(novel_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_novel_owned(db, novel_id, current_user.id)
    return db.query(Chapter).filter(Chapter.novel_id == novel_id).order_by(Chapter.chapter_number.asc()).all()


@router.post("/novels/{novel_id}/chapters", response_model=ChapterOut)
def create_chapter(novel_id: int, payload: ChapterIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    novel = get_novel_owned(db, novel_id, current_user.id)
    item = Chapter(novel_id=novel_id, **payload.model_dump())
    item.word_count = count_cn_words(item.content)
    refresh_chapter_memory(db, novel, item)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/chapters/{chapter_id}", response_model=ChapterOut)
def update_chapter(chapter_id: int, payload: ChapterIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Chapter).join(Novel).filter(Chapter.id == chapter_id, Novel.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="章节不存在")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    item.word_count = count_cn_words(item.content)
    refresh_chapter_memory(db, item.novel, item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/chapters/{chapter_id}")
def delete_chapter(chapter_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Chapter).join(Novel).filter(Chapter.id == chapter_id, Novel.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="章节不存在")
    db.delete(item)
    db.commit()
    return {"message": "已删除"}


@router.post("/ai/chapters/{chapter_id}/{mode}")
def chapter_ai_action(chapter_id: int, mode: str, payload: AIRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    mode = {"continue": "续写", "polish": "润色", "rewrite": "改写"}.get(mode, mode)
    if mode not in {"续写", "润色", "改写"}:
        raise HTTPException(status_code=400, detail="不支持的操作")
    chapter = db.query(Chapter).join(Novel).filter(Chapter.id == chapter_id, Novel.user_id == current_user.id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    result = ai_service.revise(mode, chapter, payload.instruction)
    save_ai_record(db, current_user.id, chapter.novel_id, mode, payload.model_dump(), result)
    return result


@router.get("/novels/{novel_id}/submission-preview")
def submission_preview(novel_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    novel = get_novel_owned(db, novel_id, current_user.id)
    chapters = db.query(Chapter).filter(Chapter.novel_id == novel.id).order_by(Chapter.chapter_number.asc()).all()
    preview = {
        "title": novel.title,
        "author_name": current_user.pen_name or current_user.username,
        "synopsis": novel.synopsis,
        "category": novel.genre,
        "tags": novel.tags,
        "chapters": [{"id": item.id, "title": item.title, "content": item.content} for item in chapters],
    }
    return preview


@router.get("/submissions", response_model=list[SubmissionOut])
def list_submissions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(SubmissionRecord).filter(SubmissionRecord.user_id == current_user.id).order_by(SubmissionRecord.updated_at.desc()).all()


@router.post("/submissions", response_model=SubmissionOut)
def create_submission(payload: SubmissionIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    novel = get_novel_owned(db, payload.novel_id, current_user.id)
    if payload.chapter_id:
        get_chapter_owned(db, payload.chapter_id, novel.id)
    item = SubmissionRecord(user_id=current_user.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/submissions/{submission_id}", response_model=SubmissionOut)
def update_submission(submission_id: int, payload: SubmissionIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(SubmissionRecord).filter(SubmissionRecord.id == submission_id, SubmissionRecord.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="投稿记录不存在")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/submissions/{submission_id}")
def delete_submission(submission_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(SubmissionRecord).filter(SubmissionRecord.id == submission_id, SubmissionRecord.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="投稿记录不存在")
    db.delete(item)
    db.commit()
    return {"message": "已删除"}


@router.get("/ai-records", response_model=list[AIRecordOut])
def list_ai_records(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(AIGenerationRecord).filter(AIGenerationRecord.user_id == current_user.id).order_by(AIGenerationRecord.created_at.desc()).all()


@router.get("/ai-metrics")
def ai_metrics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(AIGenerationRecord).filter(AIGenerationRecord.user_id == current_user.id).all()
    total = len(records)
    total_tokens = sum(item.total_tokens or 0 for item in records)
    total_duration = sum(item.ai_duration_ms or 0 for item in records)
    failed = sum(1 for item in records if not item.ai_success)
    retried = sum(item.retry_count or 0 for item in records)
    by_type = defaultdict(lambda: {"count": 0, "tokens": 0, "failed": 0})
    for item in records:
        bucket = by_type[item.generation_type]
        bucket["count"] += 1
        bucket["tokens"] += item.total_tokens or 0
        bucket["failed"] += 0 if item.ai_success else 1
    return {
        "summary": {
            "ai_call_count": total,
            "failed_count": failed,
            "retry_count": retried,
            "total_tokens": total_tokens,
            "avg_duration_ms": int(total_duration / total) if total else 0,
        },
        "by_type": [{"generation_type": key, **value} for key, value in by_type.items()],
    }


@router.get("/stats")
def stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    novels = db.query(Novel).filter(Novel.user_id == current_user.id).all()
    novel_ids = [item.id for item in novels]
    chapters = db.query(Chapter).filter(Chapter.novel_id.in_(novel_ids)).all() if novel_ids else []
    ai_count = db.query(func.count(AIGenerationRecord.id)).filter(AIGenerationRecord.user_id == current_user.id).scalar() or 0
    ai_records = db.query(AIGenerationRecord).filter(AIGenerationRecord.user_id == current_user.id).all()
    genre_counter = defaultdict(int)
    for novel in novels:
        genre_counter[novel.genre] += 1
    return {
        "summary": {
            "novel_count": len(novels),
            "chapter_count": len(chapters),
            "total_words": sum(item.word_count for item in chapters),
            "ai_count": ai_count,
            "pending_upload_count": sum(1 for item in chapters if item.status == "???"),
            "uploaded_count": sum(1 for item in chapters if item.status == "???"),
            "ai_failed_count": sum(1 for item in ai_records if not item.ai_success),
            "ai_retry_count": sum(item.retry_count or 0 for item in ai_records),
            "ai_total_tokens": sum(item.total_tokens or 0 for item in ai_records),
            "ai_avg_duration_ms": int(sum(item.ai_duration_ms or 0 for item in ai_records) / len(ai_records)) if ai_records else 0,
        },
        "genre_distribution": [{"name": key, "value": value} for key, value in genre_counter.items()],
    }


@router.get("/exports/{novel_id}/txt")
def export_txt(novel_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    novel = get_novel_owned(db, novel_id, current_user.id)
    chapters = db.query(Chapter).filter(Chapter.novel_id == novel.id).all()
    file_path = export_service.export_txt(novel, chapters)
    return FileResponse(file_path, filename=file_path.name)


@router.get("/exports/{novel_id}/docx")
def export_docx(novel_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    novel = get_novel_owned(db, novel_id, current_user.id)
    chapters = db.query(Chapter).filter(Chapter.novel_id == novel.id).all()
    file_path = export_service.export_docx(novel, chapters)
    return FileResponse(file_path, filename=file_path.name)


def ensure_schema():
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    dialect = engine.dialect.name
    additions = {
        "chapters": {
            "summary": "TEXT",
            "memory_keywords": "VARCHAR(255)",
        },
        "ai_generation_records": {
            "quality_score": "INTEGER DEFAULT 0",
            "quality_report": "TEXT",
            "retry_count": "INTEGER DEFAULT 0",
            "ai_duration_ms": "INTEGER DEFAULT 0",
            "prompt_tokens": "INTEGER DEFAULT 0",
            "completion_tokens": "INTEGER DEFAULT 0",
            "total_tokens": "INTEGER DEFAULT 0",
            "ai_success": "INTEGER DEFAULT 1",
            "ai_error": "TEXT",
        },
    }
    with engine.begin() as conn:
        for table, columns in additions.items():
            if table not in table_names:
                continue
            existing = {column["name"] for column in inspector.get_columns(table)}
            for name, column_type in columns.items():
                if name in existing:
                    continue
                if dialect == "mysql" and column_type == "TEXT":
                    ddl = f"ALTER TABLE {table} ADD COLUMN {name} TEXT"
                else:
                    ddl = f"ALTER TABLE {table} ADD COLUMN {name} {column_type}"
                conn.execute(text(ddl))


def init_database():
    Base.metadata.create_all(bind=engine)
    ensure_schema()
    db = next(get_db())
    try:
        seed_default_prompt_templates(db)
    finally:
        db.close()
