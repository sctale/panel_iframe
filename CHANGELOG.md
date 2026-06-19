# Changelog

## 0.2.6 (2026-06-19)

### 安全
- `panel_iframe.js` 添加 `_escapeHtml()` 方法，对 title 和 url 进行 HTML 转义防止 XSS
- `index.html` 外部链接添加 `rel="noreferrer noopener"` 防止 `window.opener` 攻击

### 新增
- `panel_iframe.js` iframe 添加 `title` 属性（无障碍访问）
- `panel_iframe.js` 添加 ARIA 属性：`role="banner"`（工具栏）、`role="alert"`（警告）、`role="status"`（加载状态）、`aria-hidden`（装饰元素）、`aria-label`（导航按钮）
- `index.html` 添加 `role="status"`、`role="button"`、`tabindex`、`aria-label` 等无障碍属性
- `index.html` 添加键盘事件支持（Enter 键打开链接）
- `index.html` 添加 `<meta http-equiv="X-UA-Compatible">` 兼容性标签
- `index.html` 添加 `'use strict'` 严格模式

### 变更
- `panel_iframe.js` mode 比较从 `==` 改为 `===`（严格比较）
- `panel_iframe.js` 内置页面模式使用 `config.url` 原始路径（不经过 URL 规范化）
- `panel_iframe.js` iframe 加载状态改用 `.iframe-wrapper` 包裹层 + CSS `~` 兄弟选择器，修复之前 `+` 选择器不生效的问题

## 0.2.5 (2026-06-19)

### 新增
- `__init__.py` 添加 `_LOGGER` 日志记录器，记录面板添加/移除/更新/代理注册等关键操作
- `http_proxy.py` 添加 `_LOGGER` 日志记录器，记录代理请求失败和超时
- `http_proxy.py` 添加代理请求异常处理：`ClientError` 返回 502、`TimeoutError` 返回 504
- `http_proxy.py` 添加 WebSocket 代理连接失败的异常捕获
- `http_proxy.py` 添加请求超时配置 `PROXY_TIMEOUT`（30秒）
- `const.py` 添加 `PLATFORMS` 常量（HA 标准）
- `hacs.json` 添加 `zip_release` 配置
- `manifest.json` codeowners 添加 `@Sid`

### 变更
- `config_flow.py` `OptionsFlow.__init__` 添加类型注解 `entry: ConfigEntry` -> `None`
- `http_proxy.py` ClientSession 创建时传入 `timeout=PROXY_TIMEOUT`

## 0.2.4 (2026-06-19)

### 新增
- 配置流程添加面板名称唯一性检查，防止重复添加同名面板
- 配置流程添加输入验证：面板名称不能为空、链接地址不能为空
- strings.json 和翻译文件添加错误消息翻译（`empty_title`、`empty_url`、`already_configured`）

### 变更
- 移除 `config_flow.py` 中未使用的 `section` 导入
- 配置流程使用 `async_set_unique_id` + `_abort_if_unique_id_configured` 替代手动检查

## 0.2.3 (2026-06-19)

### 变更
- `http_proxy.py` ClientSession 改为类级别复用，避免每次请求创建新连接
- `http_proxy.py` 新增 `cleanup()` 方法，集成卸载时正确关闭 session
- `__init__.py` 使用 `hass.data` 替代全局变量存储静态路径注册状态
- `__init__.py` 新增 `async_remove_entry` 钩子，移除配置项时清理代理资源
- `__init__.py` 使用 `const.py` 常量替代硬编码配置键名

## 0.2.2 (2026-06-19)

### 新增
- 前端面板组件添加 iframe 加载状态指示（spinner + 文字提示）
- 前端面板组件拆分为独立渲染方法（`_renderDefault`/`_renderFullscreen`/`_renderHttpsWarning`），代码更清晰
- URL 处理逻辑提取为 `_normalizeUrl` 方法，更健壮
- HTTPS 安全提示页面优化：添加警告图标、圆角按钮、更好的视觉层次
- 全屏模式移动端导航按钮改用原生 `<button>` + 圆角阴影样式

### 变更
- `index.html` 重写：使用 IIFE 避免全局污染、添加 URL 解析错误处理、优化加载动画样式
- `panel_iframe.js` 使用 HA CSS 变量（`--divider-color`、`--secondary-text-color`、`--card-background-color` 等）替代硬编码颜色
- `panel_iframe.js` iframe 加载完成后才显示，之前是直接显示空白 iframe

## 0.2.1 (2026-06-19)

### 新增
- 新增 `const.py` 集中管理常量（DOMAIN、配置键名、默认值、模式列表）
- 新增 `strings.json` 标准 HA 翻译源文件（含 `data_description` 和 `selector` 翻译）
- 配置流程使用 HA Selectors（IconSelector、TextSelector、SelectSelector、BooleanSelector），UI 体验大幅提升
- 下拉选择模式替代原来的 vol.In，每个选项带详细描述
- 图标字段使用 IconSelector，提供图标选择器 UI
- 链接字段使用 TextSelector，提供文本输入 UI

### 变更
- 移除 `manifest.py`，改用 `const.py` + 直接读取 `manifest.json`，避免模块级实例化问题
- `config_flow.py` 使用 `ConfigFlowResult` 替代 `FlowResult`（HA 2026 新命名）
- `__init__.py` 使用 `entry.version` 替代 `manifest.VERSION` 作为缓存版本号
- `__init__.py` 从 `const.py` 导入 `DOMAIN`，不再依赖 `manifest.py`
- 翻译文件增加 `data_description` 字段，为每个配置项提供详细说明
- 翻译文件增加 `selector` 翻译，支持下拉选择模式的本地化描述

## 0.2.0 (2026-06-19)

### 新增
- 代理访问支持 HTTPS 目标站点（自动识别 URL 协议）
- 代理请求忽略 SSL 证书验证（适配自签名证书的内网服务）
- README 新增「与原版的区别」对比表
- README 新增「链接格式支持」说明
- README 新增「添加多个面板」说明
- README 新增「已知限制」章节

### 变更
- JS 面板组件修复 Shadow DOM 内 `ha-menu-button` 属性绑定问题（改用 JS 手动设置属性）
- 静态资源路径注册改为仅注册一次，避免多面板时报错
- 移除 `update_listener` 中的 `asyncio.sleep(1)`，选项更新更即时
- 移除 `config_flow.py` 中未使用的 `cv` 导入
- `package.json` 清理：移除 gitee 仓库引用、修正描述、更新版本号
- 删除过时的 Windows 批处理脚本 `build.cmd`，MDI 更新改为 npm script

### 修复
- 修复多面板场景下静态路径重复注册可能报错的问题
- 修复 Shadow DOM 内 HA 自定义元素属性无法正确传递的问题
- 修复 `http_proxy.py` 代理请求转发时未过滤 `transfer-encoding` 请求头的问题

## 0.1.0 (2026-06-19)

### 新增
- 添加 `integration_type: "service"` 到 manifest.json（HA 2026 必填项）
- 添加 `panel_custom` 到 manifest.json 依赖项
- 添加 `issue_tracker` 到 manifest.json
- 添加中文翻译文件 (zh-CN.json)
- HTTPS 环境下嵌入 HTTP 页面时显示友好提示和新标签页链接

### 变更
- manifest.json `quality_scale` 从 `internal` 改为 `bronze`（`internal` 仅适用于核心集成）
- manifest.json `documentation` 从本地路径改为 GitHub 仓库 URL
- 最低 HA 版本要求从 2024.7.0 提升至 2025.1.0
- JS 面板组件从依赖 `ha-panel-lovelace` LitElement 继承改为独立 HTMLElement + Shadow DOM（更稳定，不受 HA 内部变更影响）
- manifest.py 从使用 `homeassistant.util.json.load_json` 改为标准 `json` 模块（避免 HA 内部 API 变更影响）
- 代码风格优化：添加文档字符串、类型注解、移除未使用的变量

### 修复
- 修复 config_flow.py 中未使用的 `errors` 变量
- 修复 manifest.py 中路径拼接使用 f-string 的问题（改用 `os.path.join`）

## 2026.4.13

- 初始版本
