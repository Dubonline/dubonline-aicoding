# 架构说明

## 系统组成

```text
React / TanStack Start
        │ HTTP + SSE
FastAPI（agent/app.py）
        │
任务分类与运行调度（agent/core/runtime.py）
        │
Deep Agents 工厂（agent/server.py）
        ├─ 模型与 Prompt
        ├─ Skills 与工作区记忆
        ├─ 工具及中间件
        └─ LocalShellBackend → 独立工作区 → Gitee
        │
SQLite checkpoint + 业务 Store
```

`agent/api/routes.py` 提供任务和健康检查 API；`dashboard_routes.py` 负责界面适配。`task_intent.py` 区分分析、方案、问答与开发任务；`runtime.py` 调度执行，`streaming_runtime.py` 将模型、工具和子智能体事件整理为前端可读取的事件。

## 工作区与权限

`agent/backends/` 提供本地执行、虚拟路径映射和命令限制。Agent 使用 `/projects`、`/skills`、`/policies`、`/reviews`、`/runtimes`、`/tmp` 和 `/logs` 等虚拟路径。真实工作区由 `AI_WORKSPACE_ROOT` 指定，应与项目自身源码目录分开。

当前后端主要按 Windows shell 和路径语义实现。本地命令限制降低误操作风险，但本地后端并非操作系统级隔离沙箱。远程隔离尚未实现。

## 模型、工具与记忆

`agent/core/model.py` 创建兼容 OpenAI 协议的模型客户端；`agent/prompt.py` 定义任务规则。`agent/tools/` 包含 Gitee PR、联网搜索和 URL 抓取等工具。`agent/skills/` 描述专项工作方法，`agent/memory/workspace.md` 提供稳定的工作区知识。

Git 操作通过执行工具完成，认证由工作区的 askpass 机制注入；模型和日志不应接触 Token 明文。

## 持久化

LangGraph checkpoint 保存消息与运行状态；`agent/store/sqlite_store.py` 保存用于查询和展示的业务记录。两者职责独立，不能用业务表代替 Agent 状态恢复。业务 Store 使用锁、WAL 和 busy timeout 处理本地并发访问；当前架构面向个人、本地和低并发使用。

## 代码审查

`agent/reviewer.py` 组织审查，`reviewer_diff.py` 处理差异，`reviewer_findings.py` 整理问题，`reviewer_publish.py` 发布结果。Gitee API 参考文档用于核对平台接口。

## 当前边界

当前仅支持 Gitee 仓库和本地执行。界面中继承的 Slack、自动化及管理入口不代表对应后台能力已经完整实现。远程沙箱、多租户和其它 Git 托管平台属于后续扩展方向。

## 扩展预留

`agent/extensions/` 定义租户授权、执行后端租约与 SCM 平台契约，尚未接入现有运行链路。接口责任、具体接入位置及迁移条件见[扩展边界设计](EXTENSION_POINTS.md)。
