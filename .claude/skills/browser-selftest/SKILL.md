---
name: browser-selftest
version: 1.0.0
display_name: 浏览器实机自测
display_name_en: Browser Self-Testing
description: >
  Use chrome-use CLI to do end-to-end self-testing of this project during
  development: start the dev server, open pages in the user's real Chrome,
  snapshot refs and click UI, run assertions, archive screenshots. Use when a
  change touches UI or pages and needs real-browser verification, or when
  first installing or configuring chrome-use on a machine.
description_zh: >-
  用 chrome-use CLI 对本项目做端到端实机自测：起 dev 服务、在用户真实 Chrome 里
  开页面、快照拿 refs 并点击 UI、断言、截图存档。适用场景：改动触及 UI 或页面
  需要真实浏览器验证时；或首次在新机器上安装配置 chrome-use。
description_en: >-
  Use chrome-use CLI to do end-to-end self-testing of this project during
  development: start the dev server, open pages in the user's real Chrome,
  snapshot refs and click UI, run assertions, archive screenshots. Use when a
  change touches UI or pages and needs real-browser verification, or when
  first installing or configuring chrome-use on a machine.
---

# 浏览器实机自测（browser-selftest）

用 **chrome-use CLI**（驱动用户真实 Chrome）对 web 项目做端到端实机自测：
起服务 → open → snapshot 拿 refs → click --observe → 断言 → 截图存档 → done 收尾。

## 边界

- 只做端到端实机验证（真实浏览器行为）；单元/回归断言由项目测试命令负责，互不替代
- **实机收尾是硬性要求**：typecheck / 单测过 ≠ 渲染对（编译合法不代表渲染逻辑对）。
  触及 UI 的改动必须本技能实测收尾
- CLI 优先：能用 curl / API 验证的（健康检查、造删测试数据）不驱动浏览器
- 动手前先 `chrome-use skills get core` 加载一次用法指南；命令报错时其最后一行
  说下一步做什么，照做，不要 pipe tail / 丢 stderr

## 一、安装与配置（每台机器一次性）

```powershell
irm https://raw.githubusercontent.com/leeguooooo/chrome-use/main/install.ps1 | iex
```

验证：`chrome-use status`（native host live + extension relay up）。
异常先 `chrome-use status` / `chrome-use tab list` 自诊断。

## 二、自测工作流（日常）

### 1. 起被测服务并探活

<!-- 按项目实际替换：下面三条是 ui-design-workflow 的真实命令与地址 -->
```bash
npm run dev  # 示例占位，项目定型后改为实际启动命令                       # 起服务（后台 + 日志落盘）
curl -s -m 3 http://localhost:5173           # 健康检查 / 首页探活，期望非 5xx
```

注意：**长驻服务是 watch 模式（tsx watch / vite）时，改了服务端代码要确认已重启**——
watch 对个别变化不敏感，验收前手动重启最保险（netstat 找监听 PID → taskkill //F //PID
→ 重新拉起）。严禁 `taskkill //F //IM node.exe` 这类全杀命令。

### 2. 造/删测试数据（CLI 优先）

能用 API / 脚本造数据的走 API，不驱动浏览器填表。
curl 传含中文的 JSON body 必须用文件（`--data-binary @file`，直传 Content-Length
不匹配）。测完用 DELETE / 清理脚本回收数据。

### 3. 打开页面（先确认 URL）

```bash
chrome-use open "http://localhost:5173"
```

**坑：有的应用启动会恢复上次状态**——整页加载可能被拉回上次的页面，误判为路由
解析失败。打开后先 `chrome-use get url` 确认落在目标页；被劫持则加载完后改 hash
（不触发 reload）：

```bash
chrome-use eval "location.hash = '#/<page>'"
chrome-use wait --text "<目标标题文案>"
```

### 4. 快照与交互（核心循环）

```bash
chrome-use snapshot -i -c          # 紧凑快照拿 @eN refs
chrome-use click @eN --observe     # 点击 + 自动观察（fill/select/press/hover 同样支持 --observe）
```

- refs 从最新快照复制，**不要猜编号**；页面替换后 refs 重置（--observe 会给出新快照）
- `--observe` 的 `observed.snapshot` / `observed.changes` / `observed.text`
  通常已够断言，小页面不必每次 click 后单独 snapshot
- 等内容用条件等待（`wait --text "<文案>"` / `wait --url <url>`），不要 sleep；
  **wait 超时 ≠ 失败**——先 snapshot 看页面实际状态

### 5. 断言（按优先级）

1. `--observe` 的 observed.text / observed.changes（点击链路自带）
2. `get text <sel>` / `get count <sel>` / `extract --schema '{...}'`（表格/结构化）
3. `eval` 最后手段（页全局、computed style、返回 JSON）——eval 前先查 core 替代表
4. 截图文件大小：纯空白页几百字节，有内容通常 >10KB

断言要点：分支/接线类改动必须同时测「目标命中」与「回归无泄漏」。

### 6. 截图存档（位置参数，不是 --path）

```bash
chrome-use screenshot "dev-examples/<主题>-shots/01-场景.png"
```

约定：存 `dev-examples/`（沙盒目录，随仓库入库，运行产物除外），文件名带序号与场景。
**截图前先刷新**（`chrome-use reload --observe`）——watch 服务重启后浏览器仍持旧 HTML。

### 7. 看图验证（模型不能直接看截图时）

```bash
chrome-use screenshot "dev-examples/xx.png"
```

→ `zai_mcp_server_analyze_image` 传截图路径 + **具体**视觉断言提问
（「九宫格中心是否填充」，不要泛泛「看看对不对」）。

### 8. 结束：done 收尾

```bash
chrome-use done              # 自动关本次开的 tab（用户还要看的页面用 --keep <tab>）
```

再清理测试数据、按需停服务（netstat 找 PID + `taskkill //F //PID <pid>`）。

## 三、常见坑

| 症状 | 原因 | 处理 |
|---|---|---|
| `screenshot: unknown option '--path'` | 参数是**位置参数** | `chrome-use screenshot "<路径>"` |
| `tab_reset_failed` / relay timeout | tab 的 CDP 调试通道重置 | 按错误诊断走：`status` + `tab list` 确认 → `open` 重开 tab → 重试（screenshot 只读可重试；send/submit 类先确认效果再决定） |
| `wait --text` 超时 | 文案大小写不符 / 页面未到该状态 / 被劫持到别的页 | 先 `snapshot` 看实际状态；`get url` 确认没被劫持 |
| open 后 URL 变成上次的页面 | 应用启动恢复上次状态 | `get url` 发现后 `eval` 改 hash，不整页导航 |
| refs 失效 / 编号对不上 | 页面替换重置 refs / 用了旧快照 | 重新 `snapshot -i`，从新快照复制 refs |
| 命令报 daemon still busy | chrome-use 侧忙碌 | 等待后重查；不要重放副作用命令 |
| 页面行为是旧代码 | 服务没重启 / 浏览器持旧 HTML | 服务手动重启；截图前 `reload --observe` |
| 中文 API body 报错 | curl 直传 Content-Length 不匹配 | `--data-binary @file` |

## 四、验证完成标准

实机自测完成 = 服务探活 ok + 目标页面可达且命中（observe/get text 断言）+
回归断言无泄漏 + 截图存档 + `chrome-use done` 收尾 + 测试数据清理。
