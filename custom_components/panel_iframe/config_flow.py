"""侧边栏面板配置流程"""

from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import section
from homeassistant.helpers.selector import (
    IconSelector,
    SelectSelector,
    SelectSelectorConfig,
    SelectOptionDict,
    TextSelector,
    TextSelectorConfig,
    BooleanSelector,
    BooleanSelectorConfig,
)

from .const import (
    DOMAIN,
    CONF_ICON,
    CONF_URL,
    CONF_MODE,
    CONF_REQUIRE_ADMIN,
    CONF_PROXY_ACCESS,
    DEFAULT_ICON,
    DEFAULT_MODE,
    DEFAULT_REQUIRE_ADMIN,
    DEFAULT_PROXY_ACCESS,
    MODE_LIST,
)

MODE_OPTIONS: list[SelectOptionDict] = [
    {"value": k, "label": v} for k, v in MODE_LIST.items()
]


class PanelIframeConfigFlow(ConfigFlow, domain=DOMAIN):
    """处理配置流程"""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """处理用户步骤"""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required("title"): TextSelector(
                        TextSelectorConfig()
                    ),
                }),
            )

        return self.async_create_entry(title=user_input["title"], data=user_input)

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        """获取选项流程"""
        return PanelIframeOptionsFlow(entry)


class PanelIframeOptionsFlow(OptionsFlow):
    """处理选项流程"""

    def __init__(self, entry):
        super().__init__()
        self._entry = entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """选项流程初始步骤"""
        return await self.async_step_user(user_input)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """处理选项更新"""
        if user_input is None:
            options = self._entry.options
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_ICON, default=options.get(CONF_ICON, DEFAULT_ICON)): IconSelector(),
                    vol.Required(CONF_URL, default=options.get(CONF_URL, "")): TextSelector(
                        TextSelectorConfig()
                    ),
                    vol.Required(CONF_MODE, default=options.get(CONF_MODE, DEFAULT_MODE)): SelectSelector(
                        SelectSelectorConfig(options=MODE_OPTIONS, translation_key="mode")
                    ),
                    vol.Required(CONF_REQUIRE_ADMIN, default=options.get(CONF_REQUIRE_ADMIN, DEFAULT_REQUIRE_ADMIN)): BooleanSelector(
                        BooleanSelectorConfig()
                    ),
                    vol.Required(CONF_PROXY_ACCESS, default=options.get(CONF_PROXY_ACCESS, DEFAULT_PROXY_ACCESS)): BooleanSelector(
                        BooleanSelectorConfig()
                    ),
                }),
            )

        # 选项更新
        user_input[CONF_ICON] = user_input[CONF_ICON].strip().replace("mdi-", "mdi:")
        user_input[CONF_URL] = user_input[CONF_URL].strip()

        # 内置页面禁止使用代理
        if user_input[CONF_MODE] == "3":
            user_input[CONF_PROXY_ACCESS] = False

        return self.async_create_entry(title="", data=user_input)
