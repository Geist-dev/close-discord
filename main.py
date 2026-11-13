"""Close Bot entry point. `--check` loads every cog without a Discord login."""
import argparse
import asyncio
import logging

import disnake
from disnake.ext import commands

from settings import ROOT, bot_token, test_guild_ids
from utils.databases import UsersDataBase

log = logging.getLogger('closebot')


class CloseBot(commands.InteractionBot):
    def __init__(self, *, offline=False):
        self.allowed_guild_ids = frozenset(test_guild_ids())
        flags = commands.CommandSyncFlags.default()
        if self.allowed_guild_ids:
            flags.sync_global_commands = False
        if offline:
            flags = commands.CommandSyncFlags.none()
        intents = disnake.Intents.default()
        intents.members = True
        # Slash commands and components do not need Message Content or Presence.
        super().__init__(
            intents=intents, test_guilds=list(self.allowed_guild_ids) or None,
            command_sync_flags=flags,
            allowed_mentions=disnake.AllowedMentions(everyone=False, roles=True, users=True),
        )

    def dispatch(self, event_name, *args, **kwargs):
        if self.allowed_guild_ids and args:
            subject = args[0]
            guild = subject if isinstance(subject, disnake.Guild) else getattr(subject, 'guild', None)
            guild_id = getattr(guild, 'id', None) or getattr(subject, 'guild_id', None)
            if guild_id is not None and guild_id not in self.allowed_guild_ids:
                return
        super().dispatch(event_name, *args, **kwargs)

    async def on_ready(self):
        log.info('Close Bot connected. Command scope: %s',
                 ', '.join(map(str, self.allowed_guild_ids)) or 'all installed servers')

    async def on_slash_command_error(self, inter, error):
        if isinstance(error, commands.CheckFailure):
            message = 'Для этой команды нужны права управления сервером.'
        else:
            log.error('Slash command failed: %s', type(error).__name__)
            message = 'Не удалось выполнить команду. Проверьте настройку бота и его права.'
        if inter.response.is_done():
            await inter.followup.send(message, ephemeral=True)
        else:
            await inter.response.send_message(message, ephemeral=True)


async def build_bot(*, offline=False):
    await UsersDataBase().create_table()
    bot = CloseBot(offline=offline)
    try:
        for path in sorted((ROOT / 'cogs').glob('*.py')):
            if path.name not in ('select.py', '__init__.py'):
                bot.load_extension(f'cogs.{path.stem}')
        return bot
    except Exception:
        await bot.close()
        raise


async def run(check=False):
    # Validate token before building a live bot, but never print it.
    token = None if check else bot_token()
    bot = await build_bot(offline=check)
    try:
        if check:
            print(f'CHECK OK: database ready, {len(bot.extensions)} extensions loaded; no Discord login.')
        else:
            await bot.start(token)
    finally:
        await bot.close()


def main():
    parser = argparse.ArgumentParser(description='Close Bot for Discord')
    parser.add_argument('--check', action='store_true', help='validate startup without a token or network')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(name)s: %(message)s')
    logging.getLogger('disnake.gateway').setLevel(logging.WARNING)
    try:
        asyncio.run(run(args.check))
    except KeyboardInterrupt:
        pass
    except (ValueError, disnake.LoginFailure, disnake.PrivilegedIntentsRequired) as error:
        # Configuration/auth errors never dump local settings or credentials.
        print(f'Cannot start: {type(error).__name__}. Check TOKEN, TEST_GUILD_IDS and Server Members Intent.')
        raise SystemExit(1)


if __name__ == '__main__':
    main()
