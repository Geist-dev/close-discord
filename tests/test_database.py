import pytest


async def test_config_sections_merge_without_resetting_previous_values(database):
    await database.save_config_patch(123, {'admin': 321, 'log': 444})
    await database.save_config_patch(123, {'CS2': 555})
    config = await database.get_config_by_guild(123)
    assert int(config['admin']) == 321
    assert int(config['log']) == 444
    assert int(config['CS2']) == 555
    assert int(config['DOTA2']) == 0
    await database.save_config_patch(456, {'CS2': 777})
    assert int((await database.get_config_by_guild(123))['CS2']) == 555


async def test_delete_timer_only_removes_its_own_record(database):
    await database.add_user_mut(42, 123, 1, 'first')
    await database.add_user_mut(42, 456, 1, 'second')
    rows = await database.get_user_mut_vrem(2)
    await database.delete_ban_record(rows[0][0])
    remaining = await database.get_user_mut_vrem(2)
    assert len(remaining) == 1
    assert remaining[0][1] == 456


@pytest.mark.parametrize('data', [{'unknown': 1}, {'log': -1}, {'admin': 'not a number'}, {'CS2': 2**64}])
async def test_invalid_config_is_not_written(database, data):
    with pytest.raises(ValueError):
        await database.save_config_patch(123, data)
    assert await database.get_config_by_guild(123) is None
