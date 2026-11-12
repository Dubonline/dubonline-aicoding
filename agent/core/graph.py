from __future__ import annotations

from agent.core.persistence import make_checkpointer
from agent.core.settings import CHECKPOINT_DB_PATH, STORE_DB_PATH
from agent.core.task_intent import TaskKind
from agent.store import LocalSqliteStore

_store: LocalSqliteStore | None = None
_checkpointer = None


def get_store() -> LocalSqliteStore:
    """获取业务 SQLite Store。

    Store 保存的是平台业务数据，例如任务列表、仓库地址、PR URL、review findings。
    它和 LangGraph checkpoint 是两套数据：
    - Store 面向页面和业务查询。
    - Checkpoint 面向 Agent 的 thread state 和消息历史恢复。
    """

    # dubonline：我把面向页面的摘要和 Agent 恢复状态分开维护，避免 UI 查询
    # 依赖模型消息格式。未来租户隔离必须同时覆盖 Store 和 checkpoint。
    global _store
    if _store is None:
        _store = LocalSqliteStore(STORE_DB_PATH)
    return _store


def get_checkpointer():
    """获取 LangGraph SQLite checkpointer。

    checkpointer 负责保存 Agent 运行过程中的 messages、工具调用状态和 thread state。
    本项目显式把 checkpoint 写到 data/checkpoints.sqlite，支持服务重启后的状态恢复。
    """

    global _checkpointer
    if _checkpointer is None:
        _checkpointer = make_checkpointer(CHECKPOINT_DB_PATH)
    return _checkpointer


def build_agent(thread_id: str, task_kind: TaskKind = "coding"):
    """构建一个绑定 thread_id 的 DeepAgent 兼容入口。

    实际装配统一交给 `agent.server.get_agent(config)`，保留此入口供启动脚本
    和 FastAPI runtime 使用，避免维护两套模型、工具及权限配置。
    """

    from agent.server import get_agent

    return get_agent(
        {
            "configurable": {
                "thread_id": thread_id,
                "task_kind": task_kind,
                "__is_for_execution__": True,
            }
        }
    )
