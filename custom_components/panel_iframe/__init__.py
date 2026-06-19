"""侧边栏面板 - 在 Home Assistant 侧边栏添加自定义 iframe 面板"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.http import StaticPathConfig
from homeassistant.components import frontend
from homeassistant.components.panel_custom import async_register_panel
from homeassistant.helpers.issue_registry import async_create_issue, IssueSeverity
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_URL, CONF_MODE, CONF_ICON, CONF_REQUIRE_ADMIN, CONF_PROXY_ACCESS
from .http_proxy import HttpProxy

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.deprecated(DOMAIN)

STATIC_PATH_KEY = f"{DOMAIN}_static_path_registered"
PROXY_DATA_KEY = f"{DOMAIN}_proxies"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """集成设置入口（YAML 配置已弃用）"""
    if DOMAIN in config:
        async_create_issue(
            hass,
            DOMAIN,
            "yaml_deprecated",
            is_fixable=False,
            severity=IssueSeverity.WARNING,
            translation_key="yaml_deprecated",
        )
        _LOGGER.warning("YAML 配置已弃用，请通过 UI 配置流添加面板")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """设置配置项"""
    # 注册静态资源路径（仅需注册一次）
    if not hass.data.get(STATIC_PATH_KEY):
        www_path = hass.config.path("custom_components", DOMAIN, "www")
        await hass.http.async_register_static_paths(
            [StaticPathConfig("/panel_iframe_www", www_path, False)]
        )
        hass.data[STATIC_PATH_KEY] = True
        _LOGGER.debug("静态资源路径已注册: %s", www_path)

    # 添加面板
    cfg = entry.options
    url_path = entry.entry_id
    title = entry.title
    mode = cfg.get(CONF_MODE)
    icon = cfg.get(CONF_ICON)
    url = cfg.get(CONF_URL)
    require_admin = cfg.get(CONF_REQUIRE_ADMIN)
    proxy_access = cfg.get(CONF_PROXY_ACCESS, False)

    if url is not None:
        module_url = f"/panel_iframe_www/panel_iframe.js?v={entry.version}"

        if proxy_access:
            proxy = HttpProxy(url)
            proxy.register(hass.http.app.router)
            url = proxy.get_url()
            # 存储代理实例到 hass.data，便于后续清理
            hass.data.setdefault(PROXY_DATA_KEY, {})[entry.entry_id] = proxy
            _LOGGER.info("代理已注册: %s -> %s", proxy.proxy_path, proxy.proxy_host)

        await async_register_panel(
            hass,
            frontend_url_path=url_path,
            webcomponent_name="ha-panel_iframe",
            sidebar_title=title,
            sidebar_icon=icon,
            module_url=module_url,
            config={"mode": mode, "url": url},
            require_admin=require_admin,
        )
        _LOGGER.info("面板已添加: %s (模式=%s)", title, mode)

    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """配置项版本迁移"""
    _LOGGER.debug("迁移配置项从版本 %s", entry.version)

    if entry.version == 1:
        # 版本 1 → 2：无需数据变更，仅版本号升级
        # 未来如有配置结构变更，在此添加迁移逻辑
        new_version = 2
        hass.config_entries.async_update_entry(entry, version=new_version)
        _LOGGER.info("配置项已迁移到版本 %s", new_version)

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """处理选项更新"""
    _LOGGER.debug("更新面板配置: %s", entry.title)
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """重新加载配置项（HA 2025.1+ 标准）"""
    _LOGGER.debug("重新加载面板: %s", entry.title)
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载配置项"""
    url_path = entry.entry_id
    frontend.async_remove_panel(hass, url_path)
    _LOGGER.info("面板已移除: %s", entry.title)
    return True


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """移除配置项时清理"""
    # 清理该面板的代理实例
    proxies = hass.data.get(PROXY_DATA_KEY, {})
    if entry.entry_id in proxies:
        del proxies[entry.entry_id]
    # 所有代理都已移除时，关闭共享 ClientSession
    if not proxies:
        await HttpProxy.cleanup()
    _LOGGER.info("配置项已清理: %s", entry.title)
