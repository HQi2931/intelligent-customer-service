# 智能客服助手

基于 **FastAPI + Vue 3 + LangChain + RAG** 的企业级智能客服系统，支持多轮对话、知识检索增强、多智能体编排。

## 技术栈

| 层级 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + Vue Router + Axios |
| 后端 | FastAPI + SQLAlchemy + SQLite |
| AI Agent | LangChain + 多智能体编排（Supervisor / Sub-Agent） |
| 检索 | RAG（ChromaDB + BM25 混合检索） |
| 模型 | 通义千问（ChatTongyi + DashScopeEmbeddings） |
| 网关 | Nginx（前端静态资源 + API 反向代理） |
| 部署 | Docker Compose |

## 项目结构

```
.
├── frontend/              # Vue 3 前端
│   ├── src/
│   │   ├── api/           # API 请求封装
│   │   ├── components/    # 通用组件
│   │   ├── router/        # 路由配置
│   │   └── views/         # 页面（Chat / Login）
│   └── dist/              # 构建产物（Nginx 托管）
├── src/                   # Python 后端
│   ├── agent/             # Agent 核心
│   │   ├── core/          # Supervisor + Sub-Agent + 工具注册
│   │   ├── guardrails/    # 内容过滤 + 输出校验
│   │   ├── middleware/     # 监控 + Prompt 路由
│   │   └── tools/         # RAG / 报表 / 用户工具
│   ├── api/               # FastAPI 接口
│   │   ├── routes/        # auth / chat / sessions / health / metrics
│   │   ├── middleware/     # JWT / 限流 / 日志
│   │   └── schemas/       # Pydantic 模型
│   ├── db/                # 数据库（SQLAlchemy + Redis 客户端）
│   ├── model/             # LLM 模型工厂
│   ├── rag/               # 检索增强（Chunker / Hybrid Retriever）
│   └── utils/             # 配置 / 日志 / Prompt 加载
├── streamlit_app/         # Streamlit 备用前端
├── tools/                 # 运维面板
├── scripts/               # 启动脚本
├── nginx/                 # Nginx 配置
├── config/                # YAML 配置文件
├── prompts/               # Prompt 模板
├── data/                  # 知识库文档
├── tests/                 # 测试
├── docker-compose.yml     # Docker 编排
└── Dockerfile
```

## 快速开始

### 环境要求

- Python 3.13+
- Node.js 18+
- Nginx（Windows 版本已内置）

### 1. 安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

cd frontend
npm install
npm run build
cd ..
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入 `DASHSCOPE_API_KEY`。

### 3. 启动服务

**Windows（本地开发）：**

```powershell
# 启动后端
.\scripts\start_api.ps1

# 启动 Nginx（前端 + 反向代理）
.\nginx\nginx.exe
```

**Docker（生产部署）：**

```bash
docker-compose up -d
```

### 4. 访问

| 入口 | 地址 |
|---|---|
| Vue 前端 | `http://localhost` |
| API 文档 | `http://localhost:8000/docs` |
| Streamlit | `http://localhost:8501` |

## API 端点

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/api/health` | 健康检查 |
| `POST` | `/api/auth/register` | 用户注册 |
| `POST` | `/api/auth/login` | 用户登录 |
| `GET` | `/api/auth/me` | 当前用户信息 |
| `POST` | `/api/chat` | SSE 流式对话 |
| `GET` | `/api/sessions` | 会话列表 |
| `GET` | `/api/sessions/{id}/messages` | 会话历史消息 |
| `DELETE` | `/api/sessions/{id}` | 删除会话 |
| `GET` | `/api/metrics` | 系统指标 |
| `GET` | `/api/alerts` | 熔断器告警 |

## 运行测试

```bash
pytest tests/ -v
```
