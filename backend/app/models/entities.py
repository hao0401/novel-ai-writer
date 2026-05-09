from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    pen_name: Mapped[str] = mapped_column(String(80), default="")
    password_hash: Mapped[str] = mapped_column(String(255))

    novels: Mapped[list["Novel"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Novel(Base, TimestampMixin):
    __tablename__ = "novels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    genre: Mapped[str] = mapped_column(String(40), default="都市")
    style: Mapped[str] = mapped_column(String(80), default="")
    target_platform: Mapped[str] = mapped_column(String(80), default="")
    synopsis: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[str] = mapped_column(String(255), default="")
    selling_points: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(30), default="构思中")

    user: Mapped["User"] = relationship(back_populates="novels")
    characters: Mapped[list["Character"]] = relationship(back_populates="novel", cascade="all, delete-orphan")
    world_settings: Mapped[list["WorldSetting"]] = relationship(back_populates="novel", cascade="all, delete-orphan")
    outlines: Mapped[list["Outline"]] = relationship(back_populates="novel", cascade="all, delete-orphan")
    chapters: Mapped[list["Chapter"]] = relationship(back_populates="novel", cascade="all, delete-orphan")


class Character(Base, TimestampMixin):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    novel_id: Mapped[int] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    role_type: Mapped[str] = mapped_column(String(40), default="主角")
    identity: Mapped[str] = mapped_column(String(120), default="")
    personality: Mapped[str] = mapped_column(Text, default="")
    goal: Mapped[str] = mapped_column(Text, default="")
    ability: Mapped[str] = mapped_column(Text, default="")
    background: Mapped[str] = mapped_column(Text, default="")
    relation_to_protagonist: Mapped[str] = mapped_column(String(160), default="")
    plot_function: Mapped[str] = mapped_column(Text, default="")

    novel: Mapped["Novel"] = relationship(back_populates="characters")


class WorldSetting(Base, TimestampMixin):
    __tablename__ = "world_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    novel_id: Mapped[int] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"), index=True)
    world_background: Mapped[str] = mapped_column(Text, default="")
    era_environment: Mapped[str] = mapped_column(Text, default="")
    geography: Mapped[str] = mapped_column(Text, default="")
    organizations: Mapped[str] = mapped_column(Text, default="")
    hierarchy: Mapped[str] = mapped_column(Text, default="")
    power_system: Mapped[str] = mapped_column(Text, default="")
    important_rules: Mapped[str] = mapped_column(Text, default="")
    taboos: Mapped[str] = mapped_column(Text, default="")

    novel: Mapped["Novel"] = relationship(back_populates="world_settings")


class Outline(Base, TimestampMixin):
    __tablename__ = "outlines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    novel_id: Mapped[int] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"), index=True)
    outline_type: Mapped[str] = mapped_column(String(30), default="章节大纲")
    volume_title: Mapped[str] = mapped_column(String(120), default="")
    chapter_number: Mapped[int] = mapped_column(Integer, default=1)
    chapter_title: Mapped[str] = mapped_column(String(160), default="")
    chapter_goal: Mapped[str] = mapped_column(Text, default="")
    main_plot: Mapped[str] = mapped_column(Text, default="")
    conflict: Mapped[str] = mapped_column(Text, default="")
    highlight: Mapped[str] = mapped_column(Text, default="")
    cliffhanger: Mapped[str] = mapped_column(Text, default="")
    expected_words: Mapped[int] = mapped_column(Integer, default=2000)
    content: Mapped[str] = mapped_column(Text, default="")

    novel: Mapped["Novel"] = relationship(back_populates="outlines")


class Chapter(Base, TimestampMixin):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    novel_id: Mapped[int] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"), index=True)
    outline_id: Mapped[int | None] = mapped_column(ForeignKey("outlines.id", ondelete="SET NULL"), nullable=True)
    chapter_number: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(String(160))
    content: Mapped[str] = mapped_column(Text, default="")
    highlights: Mapped[str] = mapped_column(Text, default="")
    foreshadowing: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    memory_keywords: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(30), default="草稿")
    uploaded_platform: Mapped[str] = mapped_column(String(80), default="")
    word_count: Mapped[int] = mapped_column(Integer, default=0)

    novel: Mapped["Novel"] = relationship(back_populates="chapters")


class SubmissionRecord(Base, TimestampMixin):
    __tablename__ = "submission_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    novel_id: Mapped[int] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"), index=True)
    chapter_id: Mapped[int | None] = mapped_column(ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    platform: Mapped[str] = mapped_column(String(80), default="番茄小说")
    status: Mapped[str] = mapped_column(String(30), default="未整理")
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    platform_link: Mapped[str] = mapped_column(String(255), default="")
    remarks: Mapped[str] = mapped_column(Text, default="")
    compiled_content: Mapped[str] = mapped_column(Text, default="")


class AIGenerationRecord(Base):
    __tablename__ = "ai_generation_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    novel_id: Mapped[int | None] = mapped_column(ForeignKey("novels.id", ondelete="SET NULL"), nullable=True)
    generation_type: Mapped[str] = mapped_column(String(40))
    input_text: Mapped[str] = mapped_column(Text)
    output_text: Mapped[str] = mapped_column(Text)
    quality_score: Mapped[int] = mapped_column(Integer, default=0)
    quality_report: Mapped[str] = mapped_column(Text, default="")
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    ai_duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    ai_success: Mapped[int] = mapped_column(Integer, default=1)
    ai_error: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class PromptTemplate(Base, TimestampMixin):
    __tablename__ = "prompt_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_type: Mapped[str] = mapped_column(String(40), index=True)
    genre: Mapped[str] = mapped_column(String(40), default="")
    name: Mapped[str] = mapped_column(String(120), default="")
    system_prompt: Mapped[str] = mapped_column(Text, default="")
    user_template: Mapped[str] = mapped_column(Text, default="")
    enabled: Mapped[int] = mapped_column(Integer, default=1)


class KnowledgeItem(Base, TimestampMixin):
    __tablename__ = "knowledge_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    novel_id: Mapped[int | None] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(160))
    item_type: Mapped[str] = mapped_column(String(40), default="素材")
    keywords: Mapped[str] = mapped_column(String(255), default="")
    content: Mapped[str] = mapped_column(Text, default="")
