"""侧边栏面板常量定义"""

DOMAIN = "panel_iframe"

# 配置项键名
CONF_ICON = "icon"
CONF_URL = "url"
CONF_MODE = "mode"
CONF_REQUIRE_ADMIN = "require_admin"
CONF_PROXY_ACCESS = "proxy_access"

# 默认值
DEFAULT_ICON = "mdi:link-box-outline"
DEFAULT_MODE = "0"
DEFAULT_REQUIRE_ADMIN = False
DEFAULT_PROXY_ACCESS = False

# 显示模式
MODE_DEFAULT = "0"
MODE_FULLSCREEN = "1"
MODE_NEW_PAGE = "2"
MODE_BUILTIN = "3"

MODE_LIST = {
    MODE_DEFAULT: "默认",
    MODE_FULLSCREEN: "全屏",
    MODE_NEW_PAGE: "新页面",
    MODE_BUILTIN: "内置页面",
}
