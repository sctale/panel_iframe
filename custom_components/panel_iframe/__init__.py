"""侧边栏面板 - 在 Home Assistant 侧边栏添加自定义 iframe 面板"""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.http import StaticPathConfig
from homeassistant.components import frontend
from homeassistant.components.panel_custom import async_register_panel
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_URL, CONF_MODE, CONF_ICON, CONF_REQUIRE_ADMIN, CONF_PROXY_ACCESS
from .http_proxy import HttpProxy

CONFIG_SCHEMA = cv.deprecated(DOMAIN)

STATIC_PATH_KEY = f"{DOMAIN}_static_path_registered"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """设置配置项"""
    # 注册静态资源路径（仅需注册一次）
    if not hass.data.get(STATIC_PATH_KEY):
        www_path = hass.config.path("custom_components", DOMAIN, "www")
        await hass.http.async_register_static_paths(
            [StaticPathConfig("/panel_iframe_www", www_path, False)]
        )
        hass.data[STATIC_PATH_KEY] = True

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

    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """处理选项更新"""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载配置项"""
    url_path = entry.entry_id
    frontend.async_remove_panel(hass, url_path)
    return True


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """移除配置项时清理"""
    # 清理代理 session
    await HttpProxy.cleanup()
