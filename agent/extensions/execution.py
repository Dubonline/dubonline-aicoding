"""本地与远程执行后端的生命周期契约 · dubonline · 2026年6月。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Protocol

from agent.extensions.identity import ExecutionScope

if TYPE_CHECKING:
    from deepagents.backends.protocol import SandboxBackendProtocol

BackendKind = Literal["local_shell", "remote_sandbox"]


@dataclass(frozen=True)
class BackendLease:
    """后端实例与租约分离：远程容器可以重建，任务身份和归属不能丢失。

    dubonline：我希望超时、取消、异常和重启恢复都能定位同一份租约，
    所以生命周期不能只依赖 Python 对象析构。租约中也不存 Token 明文。
    """

    lease_id: str
    scope: ExecutionScope
    kind: BackendKind
    backend: SandboxBackendProtocol


class BackendProvider(Protocol):
    """预留执行入口，不负责业务授权；acquire 前必须完成权限检查。"""

    def acquire(self, scope: ExecutionScope) -> BackendLease:
        """分配经授权的工作区；远程失败时不得隐式退回宿主机执行。

        实现方需要检查 tenant/thread/run 归属，隔离目录、凭据和网络策略。
        """
        ...

    def release(self, lease: BackendLease) -> None:
        """幂等释放租约及临时凭据；持久卷保留策略由实现方显式决定。"""
        ...
