# 侧边栏面板 (Panel Iframe)

[![hacs_badge](https://img.shields.io/badge/Home-Assistant-%23049cdb)](https://www.home-assistant.io/)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-0.3.2-blue)](https://github.com/sctale/panel_iframe)

在 Home Assistant 侧边栏添加自定义 iframe 面板，支持将任意网页嵌入到 HA 界面中。

## 致谢

本项目基于 **[@shaonianzhentan](https://github.com/shaonianzhentan)** 的原创工作 [panel_iframe](https://github.com/shaonianzhentan/panel_iframe) 开发，感谢原作者的贡献和付出！

## 与原版的区别

原版 `panel_iframe` 是 Home Assistant 内置的 YAML 配置集成，已在 HA 2024 年被移除。本改版的主要区别：

| 特性 | 原版 (HA 内置) | 本改版 |
|------|--------------|--------|
| 配置方式 | YAML (`configuration.yaml`) | UI 配置流（设置 → 集成） |
| 多面板支持 | YAML 配置多个 | 每个面板单独添加集成 |
| 动态增删 | 需重启 HA | 无需重启，即改即生效 |
| 代理访问 | 不支持 | 支持 HTTP/HTTPS 反向代理 |
| HTTPS 兼容 | 无提示 | 自动检测并提示新标签页打开 |
| MDI 图标预览 | 不支持 | 内置图标预览页面 |

## 功能特性

- 在 HA 侧边栏添加自定义网页面板
- 支持四种显示模式：默认、全屏、新页面、内置页面
- 支持代理访问，解决跨域问题（HTTP/HTTPS 均支持）
- 支持管理员可见设置
- 支持 WebSocket 代理
- HTTPS 环境下自动检测并提示安全限制
- 兼容 Home Assistant 2025.x - 2026.x

## 安装方式

### 通过 HACS 安装（推荐）

由于本插件不在 HACS 默认仓库中，需要先添加自定义仓库：

1. 打开 HACS → 右上角 ⋯ → 自定义仓库
2. 仓库地址填入：`https://github.com/sctale/panel_iframe`
3. 类别选择：集成
4. 点击添加
5. 在 HACS 中搜索「侧边栏面板」或「panel_iframe」
6. 点击安装
7. 重启 Home Assistant
8. 刷新页面

### 手动安装

1. 下载本仓库的 `custom_components/panel_iframe` 目录
2. 复制到你的 Home Assistant `custom_components/` 目录下
3. 重启 Home Assistant
4. 刷新页面

## 使用方法

### 添加面板

安装完成后，在 **设置 → 设备与服务 → 添加集成** 中搜索 `侧边栏面板` 即可。

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=panel_iframe)

1. 搜索并选择「侧边栏面板」
2. 输入面板名称（如：Node-RED）
3. 在选项中配置各项参数

### 配置项说明

| 参数 | 说明 | 示例 |
|------|------|------|
| 图标 | 侧边栏显示的图标 | `mdi:nodejs` |
| 链接 | 要嵌入的网页地址 | `http://192.168.1.100:1880` |
| 显示模式 | 面板的展示方式 | 见下方说明 |
| 管理员可见 | 仅管理员可看到此面板 | 开/关 |
| 代理访问 | 通过 HA 服务器代理请求 | 开/关 |

### 显示模式

| 模式 | 说明 |
|------|------|
| 默认 | 带 HA 顶部工具栏的 iframe 嵌入，可返回侧边栏 |
| 全屏 | 无工具栏的全屏 iframe，适合监控大屏等场景 |
| 新页面 | 在新浏览器标签页中打开链接 |
| 内置页面 | 在 HA 内部导航到指定路径（如 `/config/dashboard`） |

### 链接格式支持

链接字段支持多种简写格式，会自动补全：

| 输入 | 解析结果 |
|------|---------|
| `http://192.168.1.100:1880` | 原样使用 |
| `1880` | 自动补为 `http://当前主机:1880` |
| `//192.168.1.100:1880` | 自动补为 `当前协议://当前主机:1880` |
| `:1880/node-red/` | 自动补为 `当前协议://当前主机:1880/node-red/` |

### 代理访问

启用代理访问后，可以通过 HA 服务器代理访问内网服务，解决浏览器跨域限制：

- 内网地址：`http://192.168.1.100:1880/node-red/`
- 代理地址：`http://HA地址:8123/node-red/`

**注意事项：**
- 代理访问适用于内网 HTTP/HTTPS 服务
- 代理会忽略 SSL 证书验证（适用于自签名证书的内网服务）
- 内置页面模式自动禁用代理
- 不了解代理原理请勿勾选此选项

### 添加多个面板

本插件支持添加多个面板，每个面板是一个独立的集成实例：

1. 重复「添加面板」步骤即可
2. 每个面板可以独立配置图标、链接、模式等
3. 在集成列表中可以修改或删除单个面板

### 更新面板

1. 进入 **设置 → 设备与服务**
2. 找到对应的面板集成，点击「配置」
3. 修改参数后点击提交，面板立即生效，无需重启

### 删除面板

1. 进入 **设置 → 设备与服务**
2. 找到对应的面板集成，点击右上角 ⋯ → 删除
3. 面板立即从侧边栏移除

## 已知限制

- **HTTPS 混合内容**：当 HA 使用 HTTPS 时，无法在 iframe 中嵌入 HTTP 页面（浏览器安全限制），插件会自动提示在新标签页打开
- **部分网站禁止嵌入**：某些网站设置了 `X-Frame-Options` 或 `Content-Security-Policy` 头，会阻止被 iframe 嵌入
- **不支持 YAML 配置**：本改版仅支持 UI 配置流，不支持 `configuration.yaml` 方式

## 兼容性

| HA 版本 | 插件版本 | 状态 |
|---------|---------|------|
| 2025.1+ | 0.3.2 | 兼容 |

## 许可证

MIT License - 详见 [LICENSE](LICENSE)
