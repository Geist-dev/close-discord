from types import SimpleNamespace
from unittest.mock import AsyncMock

from cogs.join import CloseRegistrationHandler


def fake_inter(user_id):
    return SimpleNamespace(user=SimpleNamespace(id=user_id), guild=SimpleNamespace(id=123),
        response=SimpleNamespace(defer=AsyncMock()), send=AsyncMock(), edit_original_response=AsyncMock())


async def test_participant_can_leave_full_lobby(database):
    await database.add_user(10, 10, 1, 2, 3, 4, 123)
    await database.update_format('CS2_1x1_classic', 10)
    await database.update_tip(1, 10)
    await database.add_user(10, 20, 0, 0, 0, 0, 123)
    await database.add_user(10, 30, 0, 0, 0, 0, 123)
    await database.update_kol(2, 10)
    inter = fake_inter(20)
    await CloseRegistrationHandler(SimpleNamespace()).process_registration(inter, 10, 123, 'CS2')
    assert await database.get_user(20) == []
    assert (await database.get_user(10))[0][10] == 1
    inter.edit_original_response.assert_awaited_once()


async def test_new_participant_cannot_join_full_lobby(database):
    await database.add_user(10, 10, 1, 2, 3, 4, 123)
    await database.update_format('CS2_1x1_classic', 10)
    await database.update_kol(2, 10)
    inter = fake_inter(40)
    await CloseRegistrationHandler(SimpleNamespace()).process_registration(inter, 10, 123, 'CS2')
    assert await database.get_user(40) == []
    inter.send.assert_awaited_once()
    inter.edit_original_response.assert_not_awaited()


async def test_dota_first_player_can_choose_any_position(database):
    from cogs.join_dota import DotaRegistrationHandler
    await database.add_user(10, 10, 1, 2, 3, 4, 123)
    await database.update_format('DOTA2_1x1_classic', 10)
    inter = fake_inter(20)
    await DotaRegistrationHandler(SimpleNamespace()).process_dota_registration(inter, 10, 123, 5)
    assert (await database.get_user(20))[0][11] == 5
    inter.edit_original_response.assert_awaited_once()


async def test_dota_participant_can_leave_a_full_position(database):
    from cogs.join_dota import DotaRegistrationHandler
    await database.add_user(10, 10, 1, 2, 3, 4, 123)
    await database.update_format('DOTA2_1x1_classic', 10)
    for player in (20, 30):
        await database.add_user(10, player, 0, 0, 0, 0, 123)
        await database.update_rl_name(5, player)
    await database.update_kol(2, 10)
    inter = fake_inter(20)
    await DotaRegistrationHandler(SimpleNamespace()).process_dota_registration(inter, 10, 123, 5)
    assert await database.get_user(20) == []
    assert (await database.get_user(10))[0][10] == 1
