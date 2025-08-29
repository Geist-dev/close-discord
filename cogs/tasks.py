# cogs/mut_unban_task.py
from __future__ import annotations

import asyncio
from time import time as now

import disnake
from disnake.ext import commands, tasks

from utils.databases import UsersDataBase


class MutUnbanTask(commands.Cog):
    """Периодически проверяет истёкшие баны и снимает роль."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = UsersDataBase()

    # --------- единичный проход логики ---------
    async def _run_once(self):
        expired_users = await self.db.get_user_mut_vrem(int(now()))
        if not expired_users:
            return

        for row in expired_users:
            # mut: id(0), guild(1), id_user(2), timemut(3), whatmut(4)
            db_id, guild_id, user_id = int(row[0]), int(row[1]), int(row[2])

            # удаляем запись заранее, чтобы не зациклиться
            await self.db.del_user_mut(user_id)

            guild = self.bot.get_guild(guild_id)
            if guild is None:
                continue

            member = guild.get_member(user_id)

            # тянем конфиг
            conf = await self.db.get_config_by_guild(guild_id)
            if not conf:
                continue

            # роль бана
            role_id = int(conf.get("closeban_id", 0) or 0)
            role = guild.get_role(role_id) if role_id else None

            # снимаем роль, если есть
            if member and role and role in member.roles:
                try:
                    await member.remove_roles(role, reason="Истёк срок бана (авто)")
                except disnake.Forbidden:
                    print(f"❌ Нет прав для снятия роли с {member} на {guild_id}")
                except Exception as e:
                    print(f"⚠ Ошибка при снятии роли с {user_id} на {guild_id}: {e}")

            # эмбед для логов
            embed = disnake.Embed(
                title="Логи — Бан",
                description="**Снятие наказания**",
                color=disnake.Color.red(),
            )
            embed.add_field(
                name="> **Пользователь**",
                value=f"・ <@!{user_id}>\n・ {user_id}",
                inline=True,
            )
            embed.add_field(
                name="> Причина",
                value="```время бана истекло```",
                inline=False,
            )

            # лог-канал
            log_channel_id = int(conf.get("log", 0) or 0)
            log_channel = self.bot.get_channel(log_channel_id) if log_channel_id else None
            if isinstance(log_channel, (disnake.TextChannel, disnake.Thread)):
                try:
                    await log_channel.send(embed=embed)
                except Exception:
                    pass

    # --------- periodic task ---------
    @tasks.loop(minutes=1)
    async def _checker(self):
        try:
            await self._run_once()
        except Exception as e:
            print(f"[MutUnbanTask] Общая ошибка цикла: {e}")

    @_checker.before_loop
    async def _before_checker(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(1)

    # --------- жизненный цикл COG ---------
    async def cog_load(self):
        if not self._checker.is_running():
            self._checker.start()

    def cog_unload(self):
        # ВАЖНО: sync, не async
        if self._checker.is_running():
            self._checker.cancel()



def setup(bot: commands.Bot):
    bot.add_cog(MutUnbanTask(bot))
