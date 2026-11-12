# 开发指南

维护者：dubonline。

后端位于 `agent/`，前端位于 `ui/src/`，验证脚本位于 `scripts/`。安装和启动方式见项目 README。

## 修改与验证

文字和品牌修改检查受影响的引用即可；运行行为修改优先验证具体接口或模块。验证时使用临时目录和独立数据库，避免污染个人任务记录。

- 品牌与仓库选择验证：`uv run python scripts/verify_branding.py`，使用隔离目录，不调用模型。
- Python 静态检查：`uv run ruff check agent scripts`，已有问题应与本次变更区分。
- 后端基础验证：`uv run python scripts/verify_backend.py`，会构建 Agent，需要模型配置，但不会主动运行模型或推送仓库。
- 前端：在 `ui/` 下执行 `yarn typecheck`、`yarn build`；仓库规范化测试为 `yarn test src/lib/repo.test.ts`。
- 其它 `scripts/verify_*.py` 应按受影响的功能选择，先阅读脚本的外部调用和写入行为。

`verify_gitee_e2e.py` 是真实端到端操作，会调用模型、提交、推送并创建 PR。仅在明确授权的测试仓库运行，不作为日常品牌修改检查。

## 维护约定

文档描述实际实现与限制，规划能力应标记为尚未实现。示例账号使用中性占位值，服务不应内置其他人的真实仓库作为回退目标。

前端标识集中使用 `ui/public/brand.svg`。页面标题、PWA 名称、API 标题、Agent 身份及自动生成的审查文字统一使用 dubonline AI Coding。第三方依赖名称和代码来源说明按其实际来源保留。
