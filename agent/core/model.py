from __future__ import annotations

from langchain_openai import ChatOpenAI

from agent.env_utils import get_env, require_env

DEEPSEEK_V4_MAX_TOKENS = 25600


def make_main_model() -> ChatOpenAI:
    """创建编码智能体使用的 DeepSeek 模型。

    当前使用一个主模型，默认 `deepseek-v4-pro`，可通过 MAIN_MODEL 配置。
    这里不引入多模型 profile、fallback、路由器等生产级能力，
    保持模型配置与 Agent 编排的职责独立。

    显式设置 `thinking: disabled`，
    避免模型输出额外思考内容影响工具调用和最终回复。
    """

    return ChatOpenAI(
        model=get_env("MAIN_MODEL", "deepseek-v4-pro"),
        temperature=1.1,
        openai_api_key=require_env("DEEPSEEK_API_KEY"),
        openai_api_base=require_env("DEEPSEEK_BASE_URL"),
        max_tokens=DEEPSEEK_V4_MAX_TOKENS,
        streaming=True,
        extra_body={"thinking": {"type": "disabled"}},
    )

    # def make_main_model() -> BaseChatModel:
    #     return init_chat_model(
    #         model=get_env("MAIN_MODEL", "deepseek-v4-pro"),
    #         model_provider="openai",
    #         api_key=require_env("DEEPSEEK_API_KEY"),
    #         base_url=require_env("DEEPSEEK_BASE_URL"),
    #         temperature=1.1,
    #         max_tokens=DEEPSEEK_V4_MAX_TOKENS,
    #         streaming=True,
    #         extra_body={"thinking": {"type": "disabled"}},
    #     )