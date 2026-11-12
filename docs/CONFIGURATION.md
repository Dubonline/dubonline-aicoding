# 配置说明

项目根目录 `.env` 中的非空配置优先于进程环境，空值不覆盖已有环境变量。示例见 [`.env.example`](../.env.example)。

| 变量 | 用途 |
|---|---|
| `DEEPSEEK_API_KEY` | 模型服务密钥 |
| `DEEPSEEK_BASE_URL` | 模型服务 API 地址 |
| `MAIN_MODEL` | 主模型，默认 `deepseek-v4-pro` |
| `GITEE_TOKEN` | Gitee 仓库及 PR 认证 |
| `AI_WORKSPACE_ROOT` | Agent 实际工作区；请显式配置独立目录 |
| `DUBONLINE_AICODING_DEFAULT_REPO` | 可选默认 Gitee 仓库；不配置时需明确选择仓库 |
| `DUBONLINE_AICODING_DATA_DIR` | 数据目录，默认项目内 `data/` |
| `CHECKPOINT_DB_PATH` | checkpoint 文件路径 |
| `STORE_DB_PATH` | 业务 Store 文件路径 |
| `DUBONLINE_AICODING_LOG_DIR` | 日志目录，默认项目内 `logs/` |
| `DUBONLINE_AICODING_LOG_LEVEL` | 日志级别，默认 `INFO` |
| `DUBONLINE_AICODING_LOG_WHEN` | 轮转周期，默认 `midnight` |
| `DUBONLINE_AICODING_LOG_INTERVAL` | 轮转间隔，默认 `1` |
| `DUBONLINE_AICODING_LOG_RETENTION_DAYS` | 保留数量，默认 `14` |
| `DUBONLINE_AICODING_DEBUG_STREAM_EVENTS` | 设置为 `1` 开启额外流式诊断，会产生额外模型调用 |
| `VITE_DASHBOARD_API_BASE_URL` | 前端 API 地址，本地通常为 `http://127.0.0.1:2024` |

品牌更新后，项目专用配置统一使用 `DUBONLINE_AICODING_` 前缀。本地已有 `.env` 的对应键已同步迁移；若通过 IDE、系统环境或部署服务设置旧键，也需同步更新。数据文件名和数据库结构保持不变。

默认关闭 LangSmith/LangChain tracing；需要时通过进程环境或 `.env` 显式启用。不要将密钥、运行数据库或包含任务内容的日志上传到代码仓库。
