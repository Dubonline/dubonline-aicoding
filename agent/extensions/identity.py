"""租户授权边界设计 · dubonline · 2026年6月。

这些类型不构成认证或隔离实现。当前 API 和 SQLite 仍为个人模式。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

Action = Literal["read", "write", "execute", "publish", "delete"]
ResourceKind = Literal["thread", "repository", "workspace", "checkpoint", "credential"]


@dataclass(frozen=True)
class ExecutionScope:
    """由可信服务端构造的执行身份，不能直接采信请求体中的 tenant_id。

    dubonline：我把 tenant/user/thread/run 分开，是因为同一会话可以有多次执行，
    而 UUID、目录名或 thread_id 本身都不能证明资源归属。角色应由授权层查询。
    """

    tenant_id: str
    actor_id: str
    thread_id: str
    run_id: str


@dataclass(frozen=True)
class ResourceRef:
    """资源归属应从持久化记录读取，不能由调用方声明后直接放行。"""

    tenant_id: str
    kind: ResourceKind
    resource_id: str


class AuthorizationPolicy(Protocol):
    """所有读写、SSE 订阅、审批、Git 发布和凭据使用都需要经过的授权边界。"""

    def require_access(self, scope: ExecutionScope, resource: ResourceRef, action: Action) -> None:
        """拒绝或无法判断时抛出 PermissionError；不得以检查失败作为放行理由。"""
        ...
