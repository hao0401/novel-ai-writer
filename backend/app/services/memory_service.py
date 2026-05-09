from __future__ import annotations

import re
from typing import Any

from sqlalchemy.orm import Session

from ..models import Chapter, Character, KnowledgeItem, Novel, Outline, WorldSetting
from ..utils.text import compact


def chapter_memory(chapter: Chapter) -> dict[str, str]:
    text = re.sub(r"\s+", " ", chapter.content or "").strip()
    summary_source = "；".join(
        part for part in [chapter.title, chapter.highlights, chapter.foreshadowing, compact(text, 260)] if part
    )
    keywords = _keywords(" ".join([chapter.title or "", chapter.highlights or "", chapter.foreshadowing or "", text]))
    return {
        "summary": compact(summary_source, 420),
        "memory_keywords": ",".join(keywords[:12]),
    }


def build_generation_context(
    db: Session,
    novel: Novel,
    user_id: int,
    outline: Outline | None = None,
    instruction: str = "",
    history_limit: int = 8,
) -> dict[str, Any]:
    characters = db.query(Character).filter(Character.novel_id == novel.id).order_by(Character.created_at.asc()).all()
    worlds = db.query(WorldSetting).filter(WorldSetting.novel_id == novel.id).order_by(WorldSetting.created_at.desc()).all()
    outlines = db.query(Outline).filter(Outline.novel_id == novel.id).order_by(Outline.chapter_number.asc()).all()
    previous_query = db.query(Chapter).filter(Chapter.novel_id == novel.id)
    if outline:
        previous_query = previous_query.filter(Chapter.chapter_number < outline.chapter_number)
    previous_chapters = previous_query.order_by(Chapter.chapter_number.desc()).limit(history_limit).all()
    previous_chapters = list(reversed(previous_chapters))
    query_text = " ".join(
        [
            novel.title or "",
            novel.genre or "",
            novel.tags or "",
            novel.synopsis or "",
            getattr(outline, "chapter_title", "") or "",
            getattr(outline, "main_plot", "") or "",
            instruction or "",
        ]
    )
    materials = retrieve_knowledge_items(db, user_id, novel.id, query_text)
    return {
        "novel": {
            "title": novel.title,
            "genre": novel.genre,
            "style": novel.style,
            "target_platform": novel.target_platform,
            "synopsis": compact(novel.synopsis or "", 1200),
            "tags": novel.tags,
            "selling_points": compact(novel.selling_points or "", 800),
            "status": novel.status,
        },
        "characters": [_character_card(item) for item in characters],
        "world_settings": [_world_card(item) for item in worlds],
        "outline_memory": [_outline_card(item) for item in outlines],
        "current_outline": _outline_card(outline) if outline else {},
        "chapter_memories": [_chapter_card(item) for item in previous_chapters],
        "retrieved_materials": [_knowledge_card(item) for item in materials],
        "context_policy": "生成时必须优先遵守人物设定、世界观规则、历史章节摘要和素材库；如用户指令冲突，以已保存设定为准并保持剧情连续。",
    }


def retrieve_knowledge_items(db: Session, user_id: int, novel_id: int, query_text: str, limit: int = 5) -> list[KnowledgeItem]:
    items = (
        db.query(KnowledgeItem)
        .filter(KnowledgeItem.user_id == user_id, (KnowledgeItem.novel_id == novel_id) | (KnowledgeItem.novel_id.is_(None)))
        .order_by(KnowledgeItem.updated_at.desc())
        .all()
    )
    tokens = set(_keywords(query_text))
    ranked: list[tuple[int, KnowledgeItem]] = []
    for item in items:
        haystack = f"{item.title} {item.item_type} {item.keywords} {item.content}".lower()
        score = sum(1 for token in tokens if token and token.lower() in haystack)
        if score:
            ranked.append((score, item))
    if ranked:
        ranked.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in ranked[:limit]]
    return items[:limit]


def _keywords(text: str) -> list[str]:
    text = text or ""
    parts = re.split(r"[\s,，、。；;：:\n\r\t]+", text)
    cleaned: list[str] = []
    for part in parts:
        part = part.strip()
        if len(part) >= 2 and part not in cleaned:
            cleaned.append(part[:24])
    return cleaned


def _character_card(item: Character) -> dict[str, Any]:
    return {
        "name": item.name,
        "role_type": item.role_type,
        "identity": item.identity,
        "personality": compact(item.personality or "", 240),
        "goal": compact(item.goal or "", 240),
        "ability": compact(item.ability or "", 240),
        "background": compact(item.background or "", 360),
        "relation_to_protagonist": item.relation_to_protagonist,
        "plot_function": compact(item.plot_function or "", 240),
    }


def _world_card(item: WorldSetting) -> dict[str, Any]:
    return {
        "world_background": compact(item.world_background or "", 420),
        "era_environment": compact(item.era_environment or "", 240),
        "geography": compact(item.geography or "", 240),
        "organizations": compact(item.organizations or "", 300),
        "hierarchy": compact(item.hierarchy or "", 260),
        "power_system": compact(item.power_system or "", 260),
        "important_rules": compact(item.important_rules or "", 320),
        "taboos": compact(item.taboos or "", 240),
    }


def _outline_card(item: Outline | None) -> dict[str, Any]:
    if not item:
        return {}
    return {
        "chapter_number": item.chapter_number,
        "chapter_title": item.chapter_title,
        "chapter_goal": compact(item.chapter_goal or "", 220),
        "main_plot": compact(item.main_plot or "", 360),
        "conflict": compact(item.conflict or "", 220),
        "highlight": compact(item.highlight or "", 220),
        "cliffhanger": compact(item.cliffhanger or "", 220),
        "expected_words": item.expected_words,
        "content": compact(item.content or "", 420),
    }


def _chapter_card(item: Chapter) -> dict[str, Any]:
    return {
        "chapter_number": item.chapter_number,
        "title": item.title,
        "summary": item.summary or compact(item.content or "", 360),
        "memory_keywords": item.memory_keywords,
        "highlights": compact(item.highlights or "", 220),
        "foreshadowing": compact(item.foreshadowing or "", 220),
    }


def _knowledge_card(item: KnowledgeItem) -> dict[str, Any]:
    return {
        "title": item.title,
        "item_type": item.item_type,
        "keywords": item.keywords,
        "content": compact(item.content or "", 900),
    }
