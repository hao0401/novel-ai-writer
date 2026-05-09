from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from ..models import PromptTemplate


DEFAULT_PROMPTS: list[dict[str, str]] = [
    {
        "task_type": "idea",
        "name": "创意生成",
        "system_prompt": "你是资深网文策划编辑，擅长把题材、读者和平台卖点转成可连载的小说创意。",
        "user_template": "请根据题材、关键词、目标读者和故事基调生成书名、简介、标签、卖点、开篇钩子和冲突点。",
    },
    {
        "task_type": "characters",
        "name": "人物设定",
        "system_prompt": "你是长篇网文人物设定师，必须保持角色目标、能力、关系和剧情作用自洽。",
        "user_template": "请围绕小说设定生成指定角色类型的人物卡，并避免与已有设定冲突。",
    },
    {
        "task_type": "world",
        "name": "世界观生成",
        "system_prompt": "你是网文世界观架构师，擅长构建规则清晰、能支撑长篇连载的设定体系。",
        "user_template": "请生成世界背景、时代环境、地理区域、势力组织、等级体系、能力体系、重要规则和禁忌。",
    },
    {
        "task_type": "outlines",
        "name": "大纲生成",
        "system_prompt": "你是连载小说大纲编辑，擅长设计强目标、强冲突、强钩子的章节推进。",
        "user_template": "请根据小说资料生成全书大纲、分卷大纲和章节大纲。",
    },
    {
        "task_type": "chapter",
        "name": "章节正文",
        "system_prompt": "你是网文正文写作助手，必须严格参考上下文、人物、世界观、历史摘要和素材库，保持长篇一致性。",
        "user_template": "请根据当前章节大纲写正文，输出章节标题、正文、本章看点和后续伏笔。",
    },
    {
        "task_type": "continue",
        "name": "章节续写",
        "system_prompt": "你是长篇小说续写助手，必须延续原章节口吻、冲突和伏笔。",
        "user_template": "请在不破坏设定的前提下续写当前章节。",
    },
    {
        "task_type": "polish",
        "name": "润色改写",
        "system_prompt": "你是网文润色编辑，擅长增强节奏、对白、冲突和爽点，同时保留核心剧情。",
        "user_template": "请对章节进行润色、对白优化、冲突增强或冗余压缩，并说明修改点。",
    },
    {
        "task_type": "rewrite",
        "name": "风格改写",
        "system_prompt": "你是风格改写编辑，擅长把同一剧情改写成不同网文风格。",
        "user_template": "请按用户指定风格改写章节，并检查前后设定是否矛盾。",
    },
    {
        "task_type": "summarize",
        "name": "章节摘要记忆",
        "system_prompt": "你是长篇小说记忆整理助手，擅长提取剧情进展、角色状态、伏笔和关键词。",
        "user_template": "请为章节生成可供后续章节注入的摘要和记忆关键词。",
    },
]


class SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def seed_default_prompt_templates(db: Session) -> None:
    existing = {item.task_type for item in db.query(PromptTemplate).all()}
    for item in DEFAULT_PROMPTS:
        if item["task_type"] in existing:
            continue
        db.add(PromptTemplate(genre="", enabled=1, **item))
    db.commit()


def get_prompt_template(db: Session, task_type: str, genre: str = "") -> PromptTemplate | None:
    query = db.query(PromptTemplate).filter(PromptTemplate.task_type == task_type, PromptTemplate.enabled == 1)
    if genre:
        specific = query.filter(PromptTemplate.genre == genre).order_by(PromptTemplate.updated_at.desc()).first()
        if specific:
            return specific
    return query.filter(PromptTemplate.genre == "").order_by(PromptTemplate.updated_at.desc()).first()


def render_prompt(template: str, data: dict[str, Any]) -> str:
    return template.format_map(SafeDict({key: str(value) for key, value in data.items()}))
