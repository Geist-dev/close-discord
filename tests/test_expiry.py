from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import disnake
import pytest

from cogs.tasks import MutUnbanTask


def fixture_bot(*, missing_member=False):
    role = object()
    member = SimpleNamespace(roles=[role], remove_roles=AsyncMock())
    guild = SimpleNamespace(get_role=Mock(return_value=role), get_member=Mock(return_value=None if missing_member else member), fetch_member=AsyncMock(return_value=member), get_channel=Mock(return_value=None))
    bot = SimpleNamespace(get_guild=Mock(return_value=guild), allowed_guild_ids=frozenset())
    return bot, guild, member


async def test_discord_failure_retains_timer_for_retry(database):
    await database.save_config_patch(123, {'closeban_id': 7})
    await database.add_user_mut(42, 123, 1, 'test')
    bot, guild, member = fixture_bot()
    member.remove_roles.side_effect = disnake.Forbidden(SimpleNamespace(status=403, reason='Forbidden'), 'Missing permissions')
    cog = MutUnbanTask(bot)
    await cog._run_once()
    assert len(await database.get_user_mut_vrem(2)) == 1


async def test_success_removes_only_completed_timer(database):
    await database.save_config_patch(123, {'closeban_id': 7})
    await database.add_user_mut(42, 123, 1, 'test')
    bot, guild, member = fixture_bot()
    cog = MutUnbanTask(bot)
    await cog._run_once()
    member.remove_roles.assert_awaited_once()
    assert await database.get_user_mut_vrem(2) == []


async def test_uncached_member_is_fetched_before_expiry(database):
    await database.save_config_patch(123, {'closeban_id': 7})
    await database.add_user_mut(42, 123, 1, 'test')
    bot, guild, member = fixture_bot(missing_member=True)
    await MutUnbanTask(bot)._run_once()
    guild.fetch_member.assert_awaited_once_with(42)
    member.remove_roles.assert_awaited_once()


async def test_test_scope_does_not_touch_other_guilds(database):
    await database.add_user_mut(42, 456, 1, 'test')
    bot, guild, member = fixture_bot()
    bot.allowed_guild_ids = frozenset({123})
    await MutUnbanTask(bot)._run_once()
    bot.get_guild.assert_not_called()
    assert len(await database.get_user_mut_vrem(2)) == 1
