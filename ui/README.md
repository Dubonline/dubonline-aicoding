# dubonline AI Coding UI

个人 AI 编码与代码审查工作台的前端，使用 React、TypeScript、TanStack Start、Tailwind CSS 和 shadcn/ui。

## 开发

使用 `yarn.lock` 安装依赖：`yarn install --frozen-lockfile`。

将 `VITE_DASHBOARD_API_BASE_URL` 设置为后端地址（本地默认 `http://127.0.0.1:2024`），运行 `yarn dev --host 127.0.0.1`，打开 <http://127.0.0.1:3000/agents>。

`yarn typecheck` 检查类型，`yarn build` 构建，`yarn test` 运行单元测试。图标使用本地 `public/brand.svg`；部分界面组件沿用 open-swe 的实现，代码来源说明应保留。

后端配置、当前限制和数据管理见[项目 README](../README.md)。
