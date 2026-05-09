# 接口文档

系统启动后可直接访问自动接口文档：

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## 认证

系统使用 JWT Bearer Token。

- `POST /api/auth/register` 注册并返回 token
- `POST /api/auth/login` 前端 JSON 登录接口
- `POST /api/auth/token` Swagger/OAuth2 标准登录接口
- `GET /api/auth/me` 获取当前用户

请求受保护接口时添加：

```http
Authorization: Bearer <access_token>
```

## 核心接口

- 小说项目：`/api/novels`
- 人物设定：`/api/novels/{novel_id}/characters`
- 世界观：`/api/novels/{novel_id}/world-settings`
- 大纲：`/api/novels/{novel_id}/outlines`
- 章节：`/api/novels/{novel_id}/chapters`
- 投稿记录：`/api/submissions`
- AI 生成历史：`/api/ai-records`
- AI 指标统计：`/api/ai-metrics`
- 数据统计：`/api/stats`
- Prompt 模板：`/api/prompt-templates`
- 素材库：`/api/novels/{novel_id}/knowledge-items`
- TXT 导出：`/api/exports/{novel_id}/txt`
- DOCX 导出：`/api/exports/{novel_id}/docx`

## AI 接口

- `POST /api/ai/idea` 创意生成
- `POST /api/ai/characters` 人物生成
- `POST /api/ai/world` 世界观生成
- `POST /api/ai/outlines` 大纲生成
- `POST /api/ai/chapter` 章节正文生成
- `POST /api/ai/chapters/{chapter_id}/continue` 续写
- `POST /api/ai/chapters/{chapter_id}/polish` 润色
- `POST /api/ai/chapters/{chapter_id}/rewrite` 改写

## 统一异常响应

```json
{
  "code": 422,
  "message": "请求参数校验失败",
  "detail": [],
  "path": "/api/ai/chapter"
}
```

## AI 指标字段

AI 生成历史记录会保存：

- `quality_score`：生成质量分
- `quality_report`：质量说明
- `retry_count`：自动重试次数
- `ai_duration_ms`：AI 调用耗时
- `prompt_tokens`：输入 token 数
- `completion_tokens`：输出 token 数
- `total_tokens`：总 token 数
- `ai_success`：AI 调用是否成功
- `ai_error`：失败原因
