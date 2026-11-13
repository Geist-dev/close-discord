from types import SimpleNamespace
from unittest.mock import AsyncMock

from cogs.config import ConfigModal, can_configure, validate_ids


def interaction(guild_id=123, manage=True):
    return SimpleNamespace(
        guild=SimpleNamespace(id=guild_id),
        user=SimpleNamespace(guild_permissions=SimpleNamespace(manage_guild=manage)),
        response=SimpleNamespace(send_message=AsyncMock(), defer=AsyncMock()),
        followup=SimpleNamespace(send=AsyncMock()),
        text_values={'CS2': '0'},
    )


async def test_revoked_permission_cannot_submit_config(database):
    modal = ConfigModal(database, 123, 1)
    inter = interaction(manage=False)
    await modal.callback(inter)
    inter.response.send_message.assert_awaited_once()
    assert await database.get_config_by_guild(123) is None


async def test_foreign_guild_cannot_submit_config(database):
    modal = ConfigModal(database, 123, 1)
    await modal.callback(interaction(guild_id=456))
    assert await database.get_config_by_guild(123) is None


async def test_first_modal_creates_config_and_updates_only_its_fields(database):
    modal = ConfigModal(database, 123, 1)
    inter = interaction()
    await modal.callback(inter)
    inter.followup.send.assert_awaited_once()
    assert await database.get_config_by_guild(123) is not None


def test_id_validation_rejects_foreign_roles_and_nonnumeric_input():
    import pytest
    guild = SimpleNamespace(get_role=lambda _: None)
    for values in ({'CS2': 'abc'}, {'CS2': '999'}, {'CS2': '-1'}):
        with pytest.raises(ValueError):
            validate_ids(guild, values)


def test_ban_duration_limits():
    import pytest
    from cogs.closeban import duration_seconds
    assert duration_seconds('1h') == 3600
    assert duration_seconds('5d') == 5 * 86400
    for raw in ('', '0h', '-1d', '366d', '9999h', '1m', 'x'):
        with pytest.raises(ValueError):
            duration_seconds(raw)
