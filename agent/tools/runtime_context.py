from __future__ import annotations

from typing import Any

from langgraph.config import get_config

from agent.core.task_intent import TaskKind, is_read_only_task


def get_runtime_configurable() -> dict[str, Any]:
    """读取当前工具调用所属的 LangGraph configurable。

    Agent 工厂通过 `.with_config(config)` 绑定 thread、仓库和任务类型，
    工具从同一上下文读取这些信息，避免闭包和请求参数之间出现不一致。
    """

    try:
        config = get_config()
    except RuntimeError:
        return {}
    configurable = config.get("configurable", {}) if isinstance(config, dict) else {}
    return configurable if isinstance(configurable, dict) else {}


def get_runtime_thread_id() -> str | None:
    """读取当前 thread_id。"""

    value = get_runtime_configurable().get("thread_id")
    return value if isinstance(value, str) and value else None


def get_runtime_task_kind() -> TaskKind:
    """读取当前任务类型，非法值回退为 coding。"""

    value = get_runtime_configurable().get("task_kind", "coding")
    if value in {"coding", "analysis", "planning", "qa", "sync", "inspect"}:
        return value
    return "coding"


def runtime_is_read_only_task() -> bool:
    """当前任务是否为只读模式。"""

    return is_read_only_task(get_runtime_task_kind())
