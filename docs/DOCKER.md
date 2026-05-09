# Docker Compose 一键启动

## 启动

```bash
cp .env.docker.example .env
docker compose up -d --build
```

访问：

- 前端：`http://127.0.0.1:5173`
- 后端：`http://127.0.0.1:8000`
- Swagger：`http://127.0.0.1:8000/docs`
- MySQL：`127.0.0.1:3306`

## AI Key

不配置 `OPENAI_API_KEY` 时使用 mock AI，系统完整可演示。

如果使用 DeepSeek/OpenAI 兼容接口，在 `.env` 中配置：

```env
OPENAI_API_KEY=sk-xxxxxxxx
OPENAI_MODEL=deepseek-chat
OPENAI_BASE_URL=https://api.deepseek.com
```

## 常用命令

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f mysql
docker compose down
docker compose down -v
```

`docker compose down -v` 会删除 MySQL 数据卷，谨慎使用。
