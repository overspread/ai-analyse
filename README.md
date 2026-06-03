# AI 透析助手

基于 RAG（检索增强生成）的智能透析知识问答系统，支持上传 PDF/DOCX 文档，通过自然语言提问获取基于文档上下文的精准回答。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + Naive UI + Pinia |
| 后端 | Python 3.14 + FastAPI + SQLAlchemy + SQLite |
| 向量库 | ChromaDB |
| AI 模型 | NVIDIA Llama 3.1 70B Instruct（LLM）+ NV-Embed-QA-4（Embedding） |
| 文档解析 | PyMuPDF（PDF）+ python-docx（DOCX）+ jieba（中文分词） |

## 项目结构

```
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── api/            # Axios API 请求
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── views/          # 页面（Documents, Chat）
│   │   └── components/     # 组件（ChatMessages, SourceReference）
│   ├── package.json
│   └── vite.config.ts
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── main.py         # 入口
│   │   ├── config.py       # 配置
│   │   ├── database.py     # 数据库
│   │   ├── models.py       # ORM 模型
│   │   ├── schemas.py      # 数据模型
│   │   ├── routers/        # 路由（documents, chat）
│   │   └── services/       # 服务层（解析、分块、向量、LLM）
│   ├── .env                # 环境变量（不要提交到 Git）
│   └── requirements.txt
├── chroma_db/              # ChromaDB 持久化目录（自动生成）
└── .gitignore
```

## 快速开始

### 1. 后端

```bash
cd backend
pip install -r requirements.txt
```

配置环境变量，编辑 `backend/.env`：

```env
NVIDIA_API_KEY=你的NVIDIA_API密钥
```

启动服务：

```
python -m uvicorn app.main:app --reload --port 8000
```

API 文档访问 http://localhost:8000/docs

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 使用流程

1. 在 **Documents** 页面上传 PDF 或 DOCX 文档
2. 切换到 **Chat** 页面，在侧边栏选择需要查询的文档
3. 输入问题，AI 将基于选中文档生成回答并标注来源

## 注意事项

- **NVIDIA_API_KEY** 必须配置，否则无法使用 Embedding 和 LLM 功能
- 后端默认使用 SQLite，数据存储在 `backend/dialysis.db`
- ChromaDB 向量数据存储在 `chroma_db/` 目录
- 前端开发时通过 Vite 代理 `/api` 请求到后端，避免跨域问题
- 支持文件格式：`.pdf`、`.docx`，单文件最大 20MB
- `.env`、`*.db`、`node_modules/`、`__pycache__/` 已在 `.gitignore` 中排除，不会提交到 Git
