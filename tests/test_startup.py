from main import build_bot


async def test_all_extensions_load_without_network(database, monkeypatch):
    monkeypatch.setenv('TEST_GUILD_IDS', '123')
    bot = await build_bot(offline=True)
    try:
        assert len(bot.extensions) == 23
        assert bot.get_slash_command('config') is not None
        assert bot.get_slash_command('close') is not None
        assert bot.allowed_guild_ids == frozenset({123})
        assert bot.intents.members is True
        assert bot.intents.message_content is False
    finally:
        await bot.close()
