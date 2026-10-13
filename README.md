# 智能实验室预约系统

一个面向学生与实验室管理员的前后端分离预约系统。项目提供实验室与设备管理、预约提交与审核、用户管理，以及基于 LangGraph 的 AI 智能助手。AI 助手支持流式输出、知识库检索、实验室/设备查询和确认后提交预约。

## 功能特性

### 学生端

- 注册、登录和个人资料维护
- 浏览开放实验室及其设备
- 提交、查看和取消预约
- 使用 AI 助手查询实验室规则、开放时间及设备信息
- 通过多轮对话确认预约信息并提交预约

### 管理端

- 实验室信息与开放状态管理
- 设备信息与状态管理
- 用户管理
- 预约审核

### AI 助手

- 使用 LangGraph 组织模型与工具调用流程
- 通过 SSE 将思考状态、工具执行过程和回答 Token 流式推送到前端
- 使用 ChromaDB 与中文 Embedding 模型检索本地实验室知识库
- 调用真实业务工具查询实验室、设备及创建预约
- 预约落库前要求用户明确确认，避免误操作

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 前端 | Vue 3、Vite、Vue Router、Element Plus、Axios |
| 后端 | FastAPI、SQLAlchemy、Pydantic |
| 数据库 | MySQL |
| AI | LangChain、LangGraph、OpenAI-compatible API |
| 知识库 | ChromaDB、Sentence Transformers、BAAI/bge-small-zh-v1.5 |
| 鉴权 | JWT、bcrypt |

## 项目结构

```text
lab-agent/
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI 路由
│   │   ├── common/              # 通用响应与异常处理
│   │   ├── dependencies/        # 登录用户与管理员依赖
│   │   ├── models/              # SQLAlchemy 数据模型
│   │   ├── schemas/             # Pydantic 请求/响应模型
│   │   ├── services/            # 业务、Agent 与知识库逻辑
│   │   ├── utils/               # JWT 与密码工具
│   │   ├── config.py            # 环境变量配置
│   │   ├── database.py          # 数据库连接
│   │   └── main.py              # FastAPI 应用入口
│   ├── data/kb/                 # 实验室知识库 Markdown 文档
│   ├── .env.example             # 后端环境变量模板
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                 # 后端 API 封装
│   │   ├── components/          # 通用组件
│   │   ├── layouts/             # 页面布局
│   │   ├── router/              # 前端路由
│   │   ├── utils/               # 请求、鉴权与用户工具
│   │   └── views/               # 业务页面
│   ├── .env.example             # 前端环境变量模板
│   ├── package.json
│   └── vite.config.js
└── README.md
```

运行时生成的 `backend/uploads/`、`backend/data/chroma/`、前端构建产物和所有真实 `.env` 文件均不会提交到 Git。

## 开始使用

### 环境要求

- Python 3.11+
- Node.js `^22.18.0` 或 `>=24.12.0`
- MySQL 8+
- 一个兼容 OpenAI Chat Completions 的大模型 API Key

### 1. 克隆项目

```bash
git clone <your-repository-url>
cd lab-agent
```

### 2. 创建数据库

登录 MySQL 后创建数据库：

```sql
CREATE DATABASE lab_agent
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

应用启动时会通过 SQLAlchemy 自动创建所需数据表。

### 3. 配置并启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

编辑 `backend/.env`，填写数据库密码、随机 JWT 密钥和大模型 API Key。以 DeepSeek 为例：

```env
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/lab_agent?charset=utf8mb4
JWT_SECRET_KEY=replace-with-a-long-random-string
JWT_EXPIRE_HOURS=24
JWT_ALGORITHM=HS256
LLM_API_KEY=replace-with-your-api-key
LLM_MODEL=deepseek-flash
LLM_BASE_URL=https://api.deepseek.com
```

启动后端：

```bash
uvicorn app.main:app --reload --port 8000
```

接口文档默认位于 <http://127.0.0.1:8000/docs>。

### 4. 配置并启动前端

打开另一个终端：

```bash
cd frontend
npm install
cp .env.example .env.development
npm run dev
```

本地开发时 `VITE_API_BASE_URL` 默认留空，请求会由 Vite 代理到 `http://127.0.0.1:8000`。前端默认访问地址为 <http://localhost:5173>。

## 用户与管理员

通过注册页面创建的账号默认角色为 `student`。如需初始化管理员，可在开发环境中将对应数据库记录的 `role` 更新为 `admin`：

```sql
UPDATE users SET role = 'admin' WHERE username = 'your-admin-username';
```

请勿在生产环境中直接暴露数据库操作权限，应使用受保护的初始化流程创建管理员。

## AI 工作流

```text
用户问题
  -> FastAPI SSE 接口
  -> LangGraph Agent
  -> 大模型判断是否调用工具
     -> 知识库检索
     -> 实验室/设备查询
     -> 日期换算
     -> 用户确认后创建预约
  -> Token 与工具状态流式返回前端
```

知识库原始资料位于 `backend/data/kb/`。首次启动时，系统会下载并加载中文 Embedding 模型，然后在 `backend/data/chroma/` 中生成本地向量索引，因此第一次启动可能较慢。

## 安全说明

- 不要提交 `.env`、API Key、JWT 密钥或真实数据库连接串。
- 不要将上传文件、生产数据库或 Chroma 运行时索引提交到公共仓库。
- 如果密钥曾经出现在源码、注释、终端输出或 Git 历史中，应立即在对应平台撤销并重新生成。
- 部署时请收紧 CORS 来源、使用 HTTPS，并将密钥交由部署平台的 Secret 管理功能保存。

## 参考资料

- [LangGraph 文档](https://docs.langchain.com/oss/python/langgraph/overview)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Vue 文档](https://vuejs.org/)
- [LangGraph 101](https://github.com/langchain-ai/langgraph-101)

