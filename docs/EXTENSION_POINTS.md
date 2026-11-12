# 扩展边界设计

维护者：dubonline · 设计记录：2026年6月。

本文与 `agent/extensions/` 只约定后续实现需要满足的接口。当前运行链路没有导入这些协议，也没有启用租户授权、远程沙箱、GitHub 或云效客户端。现有行为仍为个人模式、本地执行和 Gitee 集成。

## 预留契约

| 方向 | 代码接口 | 责任 |
|---|---|---|
| 租户授权 | `identity.ExecutionScope`、`ResourceRef`、`AuthorizationPolicy` | 明确操作者、租户、会话、运行和资源归属；授权失败时拒绝操作 |
| 执行环境 | `execution.BackendProvider`、`BackendLease` | 获取与释放本地或远程执行环境，保留 Deep Agents 后端协议 |
| 托管平台 | `scm.SCMProvider`、`RepositoryRef`、`PullRequestRef` | 统一仓库身份、创建或复用 PR/MR、发布评论；预留 gitee/github/codeup 平台类型 |

这些 Protocol 不提供默认放行、空成功或占位网络请求。这里只能导入契约，不能据此认为系统已经获得相应能力。

## 租户权限：先确定谁在操作，再决定能读写什么

我希望身份贯穿整个任务，而不是只在 API 层增加一个 tenant_id。请求体中的租户字段不能作为认证依据；未来需要先由可信认证入口生成 ExecutionScope，并根据数据库中真实资源归属执行 require_access。

接入位置：

1. `agent/api/routes.py` 和 `dashboard_routes.py`：对创建、列表、详情、续聊、审批、删除以及 SSE 订阅统一授权。当前 `/me` 返回个人模式展示身份，管理员字段不构成认证。
2. `agent/core/runtime.py`：将已认证的 scope 传入后台任务、工具、事件和审查发布流程，重启恢复也要复核归属。
3. `agent/store/sqlite_store.py` 与 checkpoint：迁移租户字段和唯一键，使列表、查询、写入、恢复、事件订阅都按租户收敛。仅做查询过滤不够，checkpoint namespace、方案文件、日志访问也需要隔离。
4. `repo_mapping.py`、后端缓存和凭据：唯一键及缓存键包含租户和实例身份，目录与凭据均按授权作用域解析。

当前 SQLite 没有租户字段，backend 缓存仅按 thread_id，Gitee 使用个人全局凭据。本轮不迁移数据，不增加认证中间件。

## 远程沙箱：生命周期和文件操作分别约定

我保留 Deep Agents 的 SandboxBackendProtocol 作为文件和命令执行协议，把“分配哪份环境、由谁回收”单独留给 BackendProvider。这样未来可以复用 Agent 装配逻辑，不必让模型知道容器地址。

`agent/server.py` 的 `ensure_backend_for_thread` 是后续接入 acquire 的位置。运行完成、失败、超时、取消与服务重启都需要与 release 和租约恢复机制配套；释放需要幂等，持久卷保留策略需要明确。还需解除 runtime、middleware 对 LocalShellBackend、全局 WORKSPACE_ROOT 和 Path 的直接依赖，尤其不能让远程文件操作落回宿主机路径。

当前所有 thread 共享配置的本地根目录，这不提供租户级隔离。远程失败时也不应自动改用本地执行。容器镜像、网络策略、服务认证和密钥注入留待实现，具体部署方案留待后续实现。

## Gitee、GitHub 与云效：平台名称之外还要隔离实例和凭据

RepositoryRef 保留平台、host、命名空间元组、仓库名以及平台原生 ID；云效 Codeup 可以有组织和嵌套命名空间，不宜继续假定所有仓库都能拆成 owner/repo。PR 与 MR 的平台差异由适配器转换。

接入必须同时覆盖：

- API 仓库验证、前端仓库选择和 Prompt 中的能力说明。
- runtime 的仓库准备、repo_mapping 的标准地址和唯一键。
- LocalShellBackend 的 clone/askpass 与 Token 脱敏；凭据按租户和平台实例解析，凭据本身不进入 RepositoryRef、Prompt 或日志。
- `gitee_tools.py`、reviewer 的 diff 拉取和审查发布，以及事件中的平台信息。

host 需要显式可信配置，不能把模型提供的任意 URL 当作认证目的地。SCMProvider 只定义适配契约，不包含实例发现、平台 SDK、重试或限流实现。未支持的平台应明确拒绝，不能复用 Gitee Token 或静默降级。

## 后续实施顺序

先完成可信身份和持久化隔离，再接入带租约的执行环境，最后逐个平台替换 SCM 调用链。每个阶段单独迁移、验证和上线，避免三个方向同时改变任务恢复及凭据边界。
