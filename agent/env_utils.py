from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_ENV = PROJECT_ROOT / ".env"


def _load_non_empty_env(path: Path, *, override: bool) -> None:
    """加载非空配置，避免模板中的空字段覆盖已有环境变量。"""

    if not path.exists():
        return
    for key, value in dotenv_values(path).items():
        if value is None or value.strip() == "":
            continue
        if override or key not in os.environ or os.environ.get(key, "").strip() == "":
            os.environ[key] = value


def load_environment() -> None:
    """加载项目 .env，非空的本地配置优先于进程环境。"""
    _load_non_empty_env(LOCAL_ENV, override=True)

    # 本项目默认关闭 LangSmith/LangChain tracing。
    # 需要外部可观测性时可通过环境变量显式启用。
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")
    os.environ.setdefault("LANGSMITH_TRACING", "false")
    os.environ.setdefault("LANGCHAIN_API_KEY", "")


def get_env(name: str, default: str = "") -> str:
    """读取环境变量。

    这个函数每次读取前都会调用 load_environment，
    目的是让脚本、测试、Uvicorn 启动入口都能得到一致的配置加载行为。
    """

    load_environment()
    return os.environ.get(name, default)


def require_env(name: str) -> str:
    """读取必填环境变量。

    DeepSeek API Key、DeepSeek Base URL、Gitee Token 这类关键配置缺失时，
    应该尽早抛出明确错误，而不是等到模型调用或 Git push 时才失败。
    """

    value = get_env(name).strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value
