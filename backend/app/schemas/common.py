from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserCreate(BaseModel):
    username: str
    password: str
    pen_name: str = ""


class UserLogin(BaseModel):
    username: str
    password: str


class NovelIn(BaseModel):
    title: str
    genre: str = "都市"
    style: str = ""
    target_platform: str = ""
    synopsis: str = ""
    tags: str = ""
    selling_points: str = ""
    status: str = "构思中"


class NovelOut(NovelIn):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CharacterIn(BaseModel):
    name: str
    role_type: str = "主角"
    identity: str = ""
    personality: str = ""
    goal: str = ""
    ability: str = ""
    background: str = ""
    relation_to_protagonist: str = ""
    plot_function: str = ""


class CharacterOut(CharacterIn):
    id: int
    novel_id: int
    model_config = ConfigDict(from_attributes=True)


class WorldSettingIn(BaseModel):
    world_background: str = ""
    era_environment: str = ""
    geography: str = ""
    organizations: str = ""
    hierarchy: str = ""
    power_system: str = ""
    important_rules: str = ""
    taboos: str = ""


class WorldSettingOut(WorldSettingIn):
    id: int
    novel_id: int
    model_config = ConfigDict(from_attributes=True)


class OutlineIn(BaseModel):
    outline_type: str = "章节大纲"
    volume_title: str = ""
    chapter_number: int = 1
    chapter_title: str = ""
    chapter_goal: str = ""
    main_plot: str = ""
    conflict: str = ""
    highlight: str = ""
    cliffhanger: str = ""
    expected_words: int = 2000
    content: str = ""


class OutlineOut(OutlineIn):
    id: int
    novel_id: int
    model_config = ConfigDict(from_attributes=True)


class ChapterIn(BaseModel):
    outline_id: int | None = None
    chapter_number: int = 1
    title: str
    content: str = ""
    highlights: str = ""
    foreshadowing: str = ""
    summary: str = ""
    memory_keywords: str = ""
    status: str = "草稿"
    uploaded_platform: str = ""


class ChapterOut(ChapterIn):
    id: int
    novel_id: int
    word_count: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SubmissionIn(BaseModel):
    novel_id: int
    chapter_id: int | None = None
    platform: str = "番茄小说"
    status: str = "未整理"
    uploaded_at: datetime | None = None
    platform_link: str = ""
    remarks: str = ""
    compiled_content: str = ""


class SubmissionOut(SubmissionIn):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AIRequest(BaseModel):
    novel_id: int | None = None
    topic: str = ""
    keywords: str = ""
    target_readers: str = ""
    tone: str = ""
    role_type: str = "主角"
    outline_count: int = 6
    word_count: int = 1000
    writing_style: str = "都市爽文"
    chapter_id: int | None = None
    outline_id: int | None = None
    instruction: str = ""


class AIRecordOut(BaseModel):
    id: int
    novel_id: int | None
    generation_type: str
    input_text: str
    output_text: str
    quality_score: int = 0
    quality_report: str = ""
    retry_count: int = 0
    ai_duration_ms: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    ai_success: int = 1
    ai_error: str = ""
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PromptTemplateIn(BaseModel):
    task_type: str
    genre: str = ""
    name: str = ""
    system_prompt: str = ""
    user_template: str = ""
    enabled: int = 1


class PromptTemplateOut(PromptTemplateIn):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class KnowledgeItemIn(BaseModel):
    novel_id: int | None = None
    title: str
    item_type: str = "素材"
    keywords: str = ""
    content: str = ""


class KnowledgeItemOut(KnowledgeItemIn):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
