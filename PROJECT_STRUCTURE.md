# 项目结构说明

```text
novel-ai-writer/
├─ backend/                    # FastAPI 后端
│  ├─ app/
│  │  ├─ api/                  # 路由、认证依赖
│  │  ├─ models/               # SQLAlchemy 数据模型
│  │  ├─ schemas/              # Pydantic 入参/出参模型
│  │  ├─ services/             # AI、导出、上下文记忆、Prompt、质量评分服务
│  │  ├─ utils/                # JWT、安全、日志、文本工具
│  │  ├─ config.py             # 环境变量配置
│  │  └─ database.py           # 数据库连接
│  ├─ database.sql             # MySQL 建表 SQL
│  ├─ Dockerfile               # 后端容器构建
│  ├─ main.py                  # FastAPI 应用入口
│  ├─ requirements.txt         # Python 依赖
│  └─ seed.py                  # 演示数据初始化
├─ frontend/                   # Vue 3 + Vite + Element Plus 前端
│  ├─ src/
│  │  ├─ api/                  # Axios 请求封装
│  │  ├─ components/           # 通用组件
│  │  ├─ layouts/              # 主布局
│  │  ├─ router/               # 路由配置
│  │  ├─ stores/               # Pinia 状态
│  │  ├─ styles/               # 全局样式
│  │  └─ views/                # 页面
│  ├─ Dockerfile               # 前端容器构建
│  ├─ nginx.conf               # 前端静态服务和 API 代理
│  ├─ package.json
│  └─ vite.config.js
├─ docs/
│  ├─ API.md                   # 接口说明
│  ├─ AI_CONTEXT_AND_RAG.md    # 上下文、记忆、Prompt、RAG 说明
│  ├─ DOCKER.md                # Docker Compose 启动说明
│  └─ screenshots/             # GitHub README 展示截图
├─ docker-compose.yml          # MySQL + 后端 + 前端一键启动
├─ .env.docker.example         # Docker 环境变量示例
├─ .gitignore                  # 忽略本地环境、日志、构建产物和密钥
└─ README.md                   # 项目运行说明
```

## 本地运行相关但不建议提交

- `backend/.env`：本机真实环境变量，包含 DeepSeek Key，不要提交。
- `backend/.venv/`：Python 虚拟环境，可通过 `python -m venv .venv` 重建。
- `frontend/node_modules/`：前端依赖，可通过 `npm install` 重建。
- `logs/`：运行日志。
- `frontend/dist/`：前端构建产物，可通过 `npm run build` 重建。
