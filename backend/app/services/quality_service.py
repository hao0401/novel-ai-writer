from __future__ import annotations

import re
from typing import Any


def evaluate_chapter_result(result: dict[str, Any], target_words: int) -> dict[str, Any]:
    required = ["chapter_title", "content", "highlights", "foreshadowing"]
    missing = [key for key in required if not result.get(key)]
    content = re.sub(r"\s+", "", str(result.get("content") or ""))
    min_words = max(240, int(target_words * 0.35))
    score = 100
    problems: list[str] = []
    if missing:
        score -= 35
        problems.append("缺少字段：" + "、".join(missing))
    if len(content) < min_words:
        score -= 25
        problems.append(f"正文偏短：当前约 {len(content)} 字，期望至少 {min_words} 字")
    if "```" in str(result.get("content") or ""):
        score -= 10
        problems.append("正文包含 Markdown 代码块标记")
    if str(result.get("chapter_title") or "").strip().startswith("{"):
        score -= 15
        problems.append("章节标题格式异常")
    score = max(0, min(100, score))
    return {
        "score": score,
        "passed": score >= 65 and not missing,
        "report": "；".join(problems) if problems else "结构完整，达到可保存标准",
    }


def evaluate_structured_result(result: dict[str, Any], required: list[str]) -> dict[str, Any]:
    missing = [key for key in required if not result.get(key)]
    score = 100 - len(missing) * 20
    return {
        "score": max(0, score),
        "passed": not missing,
        "report": "结构完整" if not missing else "缺少字段：" + "、".join(missing),
    }
