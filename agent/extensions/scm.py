"""Gitee / GitHub / 云效 Codeup 的平台契约 · dubonline · 2026年6月。

这里只定义能力边界。当前运行时仍直接调用 Gitee 工具；没有新增平台客户端。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

from agent.extensions.identity import ExecutionScope

SCMKind = Literal["gitee", "github", "codeup"]


@dataclass(frozen=True)
class RepositoryRef:
    """平台、实例和命名空间共同确定仓库身份。

    dubonline：我不把仓库固定成 owner/repo 两段，给云效的组织和嵌套路径
    留出空间；host 用于区分托管与自建实例。clone_url 必须是不带凭据的地址，
    host 必须经过配置白名单检查，不能据此直接向任意地址发送认证请求。
    """

    provider: SCMKind
    host: str
    namespace: tuple[str, ...]
    name: str
    clone_url: str
    external_id: str | None = None


@dataclass(frozen=True)
class PullRequestRef:
    """对业务层统一 PR/MR 的引用，不暴露各平台原始响应结构。"""

    repository: RepositoryRef
    external_id: str
    web_url: str


class SCMProvider(Protocol):
    """未来适配器负责 URL 规则、凭据隔离、平台 API 以及 PR/MR 语义转换。

    每次调用按 scope 解析凭据引用，避免使用当前个人模式的全局 Gitee Token。
    Git askpass 也需要接入同一个凭据边界，不能只替换 PR 的 HTTP 客户端。
    """

    def parse_repository(self, url: str) -> RepositoryRef:
        """解析并验证受信任实例上的仓库地址；不支持的地址应明确拒绝。"""
        ...

    def ensure_pull_request(
        self,
        scope: ExecutionScope,
        repository: RepositoryRef,
        *,
        head: str,
        base: str,
        title: str,
        body: str,
    ) -> PullRequestRef:
        """按源分支与目标分支创建或复用 PR/MR；发布前验证身份与仓库权限。"""
        ...

    def post_comment(self, scope: ExecutionScope, pull_request: PullRequestRef, body: str) -> None:
        """向指定 PR/MR 发布评论，并应用对应实例的权限与限流规则。"""
        ...
