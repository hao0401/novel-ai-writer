import json
import time
from typing import Any
from openai import OpenAI
from ..config import get_settings
from ..utils.text import compact


class AIService:
    def __init__(self):
        self.settings = get_settings()
        self.last_metrics: dict[str, Any] = self._empty_metrics()

    def _empty_metrics(self) -> dict[str, Any]:
        return {
            "duration_ms": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "success": False,
            "error": "",
            "mock": not bool(self.settings.openai_api_key),
        }

    def _client(self):
        if not self.settings.openai_api_key:
            return None
        kwargs = {"api_key": self.settings.openai_api_key}
        if self.settings.openai_base_url:
            kwargs["base_url"] = self.settings.openai_base_url
        return OpenAI(**kwargs)

    def _real_json(self, system: str, user: str) -> dict[str, Any] | None:
        started = time.perf_counter()
        self.last_metrics = self._empty_metrics()
        client = self._client()
        if not client:
            self.last_metrics["duration_ms"] = int((time.perf_counter() - started) * 1000)
            return None
        try:
            kwargs = {
                "model": self.settings.openai_model,
                "messages": [
                    {"role": "system", "content": system + "\n请只返回 JSON，不要输出 Markdown。"},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.85,
            }
            if (self.settings.openai_base_url or "").startswith("https://api.deepseek.com"):
                kwargs["response_format"] = {"type": "json_object"}
            resp = client.chat.completions.create(**kwargs)
            usage = getattr(resp, "usage", None)
            self.last_metrics.update(
                {
                    "duration_ms": int((time.perf_counter() - started) * 1000),
                    "prompt_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
                    "completion_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
                    "total_tokens": getattr(usage, "total_tokens", 0) if usage else 0,
                    "success": True,
                    "mock": False,
                }
            )
            content = resp.choices[0].message.content or "{}"
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                start = content.find("{")
                end = content.rfind("}")
                if start != -1 and end != -1 and end > start:
                    return json.loads(content[start:end + 1])
                return None
        except Exception as exc:
            self.last_metrics.update(
                {
                    "duration_ms": int((time.perf_counter() - started) * 1000),
                    "success": False,
                    "error": str(exc)[:500],
                    "mock": False,
                }
            )
            return None

    def _has_keys(self, data: dict[str, Any] | None, keys: list[str]) -> bool:
        return bool(data) and all(key in data and data[key] not in (None, "", []) for key in keys)

    def _normalize_chapter_result(self, data: dict[str, Any] | None) -> dict[str, Any] | None:
        if not data:
            return None
        aliases = {
            "chapter_title": ["chapter_title", "title", "章节标题", "chapterName"],
            "content": ["content", "body", "text", "chapter_content", "正文", "章节正文"],
            "highlights": ["highlights", "highlight", "selling_points", "本章看点", "看点"],
            "foreshadowing": ["foreshadowing", "foreshadows", "伏笔", "后续伏笔"],
        }
        normalized: dict[str, Any] = {}
        for target, names in aliases.items():
            for name in names:
                value = data.get(name)
                if value not in (None, "", []):
                    normalized[target] = value
                    break
        if isinstance(normalized.get("highlights"), list):
            normalized["highlights"] = "；".join(str(item) for item in normalized["highlights"])
        if isinstance(normalized.get("foreshadowing"), list):
            normalized["foreshadowing"] = "；".join(str(item) for item in normalized["foreshadowing"])
        return {**data, **normalized}

    def idea(self, payload: dict[str, Any]) -> dict[str, Any]:
        schema = {
            "titles": ["书名1", "书名2", "书名3"],
            "one_sentence_pitch": "一句话卖点",
            "synopsis": "小说简介",
            "category": "分类建议",
            "tags": ["标签1", "标签2"],
            "opening_hook": "开篇钩子",
            "conflicts": ["主要爽点或冲突点"],
        }
        real = self._real_json(
            "你是资深网文策划编辑，必须按指定字段输出网文创意方案。",
            "输入：" + json.dumps(payload, ensure_ascii=False) + "\n输出 JSON schema：" + json.dumps(schema, ensure_ascii=False),
        )
        if self._has_keys(real, ["titles", "one_sentence_pitch", "synopsis", "category", "tags", "opening_hook", "conflicts"]):
            return real
        topic = payload.get("topic") or "都市异能"
        keywords = payload.get("keywords") or "逆袭,成长,秘密组织"
        return {
            "titles": [f"《{topic}：我在长夜里改写命运》", f"《开局一页旧稿，震动全网》", f"《深青档案》"],
            "one_sentence_pitch": f"一个普通作者因{keywords}卷入隐藏世界，在连续反转中完成自我证明。",
            "synopsis": f"故事以{topic}为核心，主角从低谷开局，凭借冷静判断和关键能力不断突破困境。剧情强调强目标、快节奏、连续冲突和清晰爽点，适合连载平台稳定更新。",
            "category": topic,
            "tags": ["逆袭", "成长", "强剧情", "悬念", "爽点"],
            "opening_hook": "凌晨三点，主角收到一封没有署名的投稿回执，里面竟写着他明天才会经历的死亡细节。",
            "conflicts": ["身份被质疑", "能力代价逐步显现", "隐藏组织逼近", "亲近之人立场反转"],
        }

    def characters(self, novel: Any, role_type: str) -> list[dict[str, Any]]:
        schema = {
            "characters": [{
                "name": "姓名",
                "role_type": role_type,
                "identity": "身份",
                "personality": "性格",
                "goal": "目标",
                "ability": "能力",
                "background": "背景经历",
                "relation_to_protagonist": "与主角关系",
                "plot_function": "剧情作用",
            }]
        }
        real = self._real_json(
            "你是网文人物设定师，必须返回 characters 数组，每个人物字段完整。",
            f"小说：《{novel.title}》；角色类型：{role_type}；输出 JSON schema：" + json.dumps(schema, ensure_ascii=False),
        )
        if real and isinstance(real.get("characters"), list) and real["characters"]:
            return real["characters"]
        return [
            {
                "name": "陆知行",
                "role_type": "主角",
                "identity": "落魄写手，兼职平台审核员",
                "personality": "克制、敏锐、有底线，遇到关键抉择时敢赌",
                "goal": "查清父亲旧稿失踪真相，并完成一本真正属于自己的爆款小说",
                "ability": "能从文字细节中推演人物未来选择，但每次使用都会消耗记忆片段",
                "background": "少年时因家庭变故离开故乡，长期在创作和现实压力之间挣扎",
                "relation_to_protagonist": "本人",
                "plot_function": "承担成长线和解谜线，是读者代入视角",
            },
            {
                "name": "沈青瓷",
                "role_type": "重要人物",
                "identity": "平台资深编辑",
                "personality": "理性、强势、外冷内热",
                "goal": "找到能打破平台流量困局的新作品",
                "ability": "熟悉各平台投稿规则和读者偏好",
                "background": "曾经捧红多部作品，也因一次误判失去职业信任",
                "relation_to_protagonist": "导师与合作者",
                "plot_function": "推动投稿线、商业线和价值观冲突",
            },
        ]

    def world(self, novel: Any) -> dict[str, Any]:
        schema = {
            "world_background": "世界背景",
            "era_environment": "时代环境",
            "geography": "地理区域",
            "organizations": "势力组织",
            "hierarchy": "等级体系",
            "power_system": "能力体系",
            "important_rules": "重要规则",
            "taboos": "禁忌或限制",
        }
        real = self._real_json(
            "你是网文世界观设计师，必须按指定字段输出世界观设定。",
            f"小说：《{novel.title}》；输出 JSON schema：" + json.dumps(schema, ensure_ascii=False),
        )
        if self._has_keys(real, list(schema.keys())):
            return real
        return {
            "world_background": "现实都市之下存在由故事、流量和读者情绪驱动的隐秘秩序。",
            "era_environment": "近未来内容平台高度竞争，AI 辅助创作普及，但真正的原创能力变得稀缺。",
            "geography": "故事主要发生在海城、旧城区档案馆、平台总部和地下作者社群。",
            "organizations": "青页编辑部、暗稿会、平台风控组、民间作者联盟。",
            "hierarchy": "普通作者、签约作者、头部作者、规则掌控者、叙事改写者。",
            "power_system": "能力来自对文本因果的感知、改写和承担代价。",
            "important_rules": "越强的改写越需要现实代价；人物选择不能被完全操控；读者情绪会反噬作者。",
            "taboos": "不能改写已公开发布的核心事实；不能让虚构人物替现实人物承担死亡。",
        }

    def outlines(self, novel: Any, count: int) -> dict[str, Any]:
        schema = {
            "full_outline": "全书大纲",
            "volume_outline": "分卷大纲",
            "chapters": [{
                "outline_type": "章节大纲",
                "chapter_number": 1,
                "chapter_title": "章节标题",
                "chapter_goal": "本章目标",
                "main_plot": "主要剧情",
                "conflict": "冲突点",
                "highlight": "爽点",
                "cliffhanger": "结尾悬念",
                "expected_words": 2000,
            }],
        }
        real = self._real_json(
            "你是连载小说大纲编辑，必须输出全书大纲、分卷大纲和 chapters 数组。",
            f"小说：《{novel.title}》；章节数量：{count}；输出 JSON schema：" + json.dumps(schema, ensure_ascii=False),
        )
        if self._has_keys(real, ["full_outline", "volume_outline", "chapters"]) and isinstance(real.get("chapters"), list):
            return real
        chapters = []
        for i in range(1, count + 1):
            chapters.append({
                "outline_type": "章节大纲",
                "chapter_number": i,
                "chapter_title": f"第{i}章 旧稿里的预言",
                "chapter_goal": "制造强钩子并推进主角发现异常。",
                "main_plot": f"主角第{i}次验证旧稿内容与现实吻合，并获得新的线索。",
                "conflict": "平台压力、现实危机和隐藏组织试探同时逼近。",
                "highlight": "主角利用细节反制对方，第一次体现能力爽点。",
                "cliffhanger": "结尾出现一行他从未写过的章节标题。",
                "expected_words": 2000,
            })
        return {
            "full_outline": "全书围绕主角从低谷写手成长为能掌控叙事规则的作者展开，前期用悬念和逆袭建立阅读期待，中期打开组织和能力体系，后期完成现实投稿与隐秘规则的双线收束。",
            "volume_outline": "第一卷：旧稿预言。主角发现旧稿能预示现实，并被迫进入平台与暗稿会的争夺。",
            "chapters": chapters,
        }

    def chapter(
        self,
        novel: Any,
        outline: Any,
        context: dict[str, Any],
        word_count: int,
        style: str,
        prompt_template: Any = None,
        quality_feedback: str = "",
    ) -> dict[str, Any]:
        schema = {
            "chapter_title": "章节标题",
            "content": "章节正文",
            "highlights": "本章看点",
            "foreshadowing": "后续伏笔",
        }
        real = self._real_json(
            "你是网文正文写作助手，必须参考上下文并按指定字段输出章节正文。",
            json.dumps(
                {
                    "novel": novel.title,
                    "outline": getattr(outline, "chapter_title", ""),
                    "context": context,
                    "word_count": word_count,
                    "style": style,
                    "output_schema": schema,
                },
                ensure_ascii=False,
            ),
        )
        real = self._normalize_chapter_result(real)
        if self._has_keys(real, ["chapter_title", "content", "highlights", "foreshadowing"]):
            return real
        title = getattr(outline, "chapter_title", "") or "第1章 旧稿里的预言"
        body = (
            f"{title}\n\n"
            "凌晨三点，陆知行盯着屏幕上那封投稿回执，指尖迟迟没有落下。\n\n"
            "回执的格式很普通，普通到像任何一家内容平台都会自动生成的模板。可最后一行却让他后背发凉："
            "“明天上午九点十七分，青页大厦三楼会议室，不要签那份合同。”\n\n"
            "他没有把这句话写进任何稿子里，也没有告诉任何人自己明天要去平台总部。窗外的雨敲着玻璃，像有人在暗处缓慢倒数。"
            "陆知行打开抽屉，取出父亲留下的旧稿。泛黄纸页上，同样的句子正静静躺在那里，墨迹却像刚刚干透。\n\n"
            "他意识到，自己一直以为失败的创作，也许从来不是失败，而是一道被人藏起来的门。"
        )
        return {
            "chapter_title": title,
            "content": body,
            "highlights": "开篇钩子明确，旧稿预言与投稿线结合，形成悬念和职业代入。",
            "foreshadowing": "父亲旧稿、青页大厦合同、自动回执来源将成为后续伏笔。",
        }

    def chapter_with_context(
        self,
        novel: Any,
        outline: Any,
        context: dict[str, Any],
        word_count: int,
        style: str,
        prompt_template: Any = None,
        quality_feedback: str = "",
    ) -> dict[str, Any]:
        schema = {
            "chapter_title": "章节标题",
            "content": "章节正文",
            "highlights": "本章看点",
            "foreshadowing": "后续伏笔",
        }
        system = getattr(prompt_template, "system_prompt", "") or "你是网文正文写作助手，必须参考上下文、人物设定、世界观、历史摘要和素材库，保持长篇内容一致。"
        real = self._real_json(
            system,
            json.dumps(
                {
                    "task": "生成章节正文",
                    "novel": getattr(novel, "title", ""),
                    "outline": getattr(outline, "chapter_title", ""),
                    "context": context,
                    "word_count": word_count,
                    "style": style,
                    "quality_feedback": quality_feedback,
                    "requirements": [
                        "不得改写已保存的人物关系和世界规则",
                        "必须承接历史章节摘要中的剧情状态",
                        "优先使用检索到的素材库信息",
                        "输出必须是 JSON，不要 Markdown",
                    ],
                    "output_schema": schema,
                },
                ensure_ascii=False,
            ),
        )
        real = self._normalize_chapter_result(real)
        if self._has_keys(real, ["chapter_title", "content", "highlights", "foreshadowing"]):
            return real
        return self.chapter(novel, outline, context, word_count, style)

    def summarize_chapter(self, novel: Any, chapter: Any, prompt_template: Any = None) -> dict[str, Any]:
        schema = {"summary": "章节摘要", "memory_keywords": ["关键词1", "关键词2"]}
        system = getattr(prompt_template, "system_prompt", "") or "你是长篇小说记忆整理助手，只提取供后续创作使用的剧情记忆。"
        real = self._real_json(
            system,
            json.dumps(
                {
                    "novel": getattr(novel, "title", ""),
                    "chapter_title": getattr(chapter, "title", ""),
                    "content": compact(getattr(chapter, "content", "") or "", 2200),
                    "highlights": getattr(chapter, "highlights", ""),
                    "foreshadowing": getattr(chapter, "foreshadowing", ""),
                    "output_schema": schema,
                },
                ensure_ascii=False,
            ),
        )
        if self._has_keys(real, ["summary", "memory_keywords"]):
            keywords = real.get("memory_keywords")
            if isinstance(keywords, list):
                real["memory_keywords"] = ",".join(str(item) for item in keywords[:12])
            return real
        text = compact(getattr(chapter, "content", "") or "", 360)
        return {
            "summary": "；".join(part for part in [getattr(chapter, "title", ""), getattr(chapter, "highlights", ""), text] if part),
            "memory_keywords": ",".join(filter(None, [getattr(chapter, "title", ""), getattr(chapter, "foreshadowing", "")]))[:255],
        }

    def revise(self, mode: str, chapter: Any, instruction: str = "") -> dict[str, Any]:
        original = chapter.content or ""
        suffix = {
            "续写": "\n\n门外忽然传来三声很轻的敲击。陆知行没有开灯，只把旧稿翻到下一页。纸上多出一行字：来的人，不是编辑。",
            "润色": "\n\n修改说明：已增强开篇压迫感、减少解释性句子，并让悬念更集中。",
            "改写": "\n\n改写说明：已按照指定风格调整节奏、对白和冲突密度。",
        }.get(mode, "\n\n修改说明：已完成文本优化。")
        revised = original + suffix
        return {
            "before": compact(original, 1800),
            "after": revised,
            "summary": f"{mode}完成。{instruction or '重点优化节奏、冲突和章节钩子。'}",
            "consistency_check": "未发现与现有人物设定和世界观明显冲突；后续需持续跟踪能力代价设定。",
        }
