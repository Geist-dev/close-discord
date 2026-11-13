"""Expire Closeban roles without losing retry records on Discord failures."""
import logging
from time import time as now

import disnake
from disnake.ext import commands, tasks

from utils.databases import UsersDataBase

log = logging.getLogger('closebot.expiry')


class MutUnbanTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = UsersDataBase()

    async def _run_once(self):
        for row in await self.db.get_user_mut_vrem(int(now())):
            record_id, guild_id, user_id = map(int, row[:3])
            allowed = getattr(self.bot, 'allowed_guild_ids', ())
            if allowed and guild_id not in allowed:
                continue
            try:
                await self._expire_one(record_id, guild_id, user_id)
            except (disnake.HTTPException, ValueError, TypeError) as error:
                # Preserve the row; another user's timer must still be processed.
                log.warning('Role removal postponed for guild=%s user=%s (%s)', guild_id, user_id, type(error).__name__)

    async def _expire_one(self, record_id, guild_id, user_id):
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return
        config = await self.db.get_config_by_guild(guild_id)
        if not config or not int(config.get('closeban_id') or 0):
            return
        role = guild.get_role(int(config['closeban_id']))
        if role is None:
            return
        member = guild.get_member(user_id)
        if member is None:
            try:
                member = await guild.fetch_member(user_id)
            except disnake.NotFound:
                # User left the guild; no role remains to remove.
                await self.db.delete_ban_record(record_id)
                return
        if role in member.roles:
            await member.remove_roles(role, reason='Истёк срок Closeban')
        # Delete only this timer, after the role is absent or successfully removed.
        await self.db.delete_ban_record(record_id)
        channel = guild.get_channel(int(config.get('log') or 0))
        if channel is not None:
            embed = disnake.Embed(title='Closeban завершён', description=f'Участник <@{user_id}> · срок ограничения истёк.', color=0xB8E89B)
            embed.set_footer(text='Close Bot · Geist-dev')
            try:
                await channel.send(embed=embed, allowed_mentions=disnake.AllowedMentions.none())
            except disnake.HTTPException:
                log.warning('Could not send expiry log for guild=%s user=%s', guild_id, user_id)

    @tasks.loop(minutes=1)
    async def _checker(self):
        try:
            await self._run_once()
        except Exception as error:
            log.error('Expiry pass failed (%s); will retry.', type(error).__name__)

    @_checker.before_loop
    async def _before_checker(self):
        await self.bot.wait_until_ready()

    async def cog_load(self):
        if not self._checker.is_running():
            self._checker.start()

    def cog_unload(self):
        self._checker.cancel()


def setup(bot):
    bot.add_cog(MutUnbanTask(bot))
