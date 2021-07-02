"""Test the MyJDownloader config flow."""
from unittest.mock import patch

from homeassistant import config_entries, data_entry_flow, setup
from homeassistant.components.myjdownloader.config_flow import (
    CannotConnect,
    InvalidAuth,
)
from homeassistant.components.myjdownloader.const import DOMAIN
from homeassistant.core import HomeAssistant


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["errors"] is None

    with patch(
        "homeassistant.components.myjdownloader.MyJDownloaderHub.authenticate",
        return_value=True,
    ), patch(
        "homeassistant.components.myjdownloader.MyJDownloaderHub.update_jdownloaders",
        return_value=[],
    ), patch(
        "homeassistant.components.myjdownloader.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "email": "test@test.com",
                "password": "test-password",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
    assert result2["title"] == "MyJDownloader"
    assert result2["data"] == {
        "email": "test@test.com",
        "password": "test-password",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_auth(hass: HomeAssistant) -> None:
    """Test we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "homeassistant.components.myjdownloader.config_flow.validate_input",
        side_effect=InvalidAuth,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "email": "test@test.com",
                "password": "test-password",
            },
        )

    assert result2["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "invalid_auth"}


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "homeassistant.components.myjdownloader.config_flow.validate_input",
        side_effect=CannotConnect,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "email": "test@test.com",
                "password": "test-password",
            },
        )

    assert result2["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "cannot_connect"}
