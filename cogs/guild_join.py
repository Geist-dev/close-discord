# cogs/guild_join_notifier.py
from __future__ import annotations

import asyncio
import disnake
from disnake.ext import commands
from datetime import datetime, timezone


class GuildJoinNotifier(commands.Cog):
    """
    При входе бота на сервер:
      • ищем в аудит-логе, кто добавил бота (AuditLogAction.bot_add)
      • отправляем эмбед в ЛС добавившему и овнеру (если это разные пользователи)
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: disnake.Guild):
        await asyncio.sleep(2)  # небольшая задержка, чтобы аудит-лог успел записаться

        adder = await self._try_get_adder(guild)
        owner = guild.owner

        # формируем эмбед с инструкциями
        embed = disnake.Embed(
            title="👋 Спасибо за добавление бота!",
            description=(
                f"Сервер: **{guild.name}** (`{guild.id}`)\n\n"
                "Чтобы всё заработало корректно, сделайте 2 шага:\n"
                "1) **Выдайте боту роль с правами администратора** и поднимите её **выше** всех ролей, "
                "которые вы будете указывать в конфиге (иначе у бота могут быть ограничения по правам).\n"
                "2) Введите команду **`/config`** на сервере и **заполните** параметры.\n\n"
                "После сохранения конфига — можно пользоваться функционалом сразу через команду **`/close create`**."
            ),
            timestamp=datetime.now(timezone.utc),
        )
        embed.set_footer(text="Если ЛС закрыты — откройте их на время, чтобы получить инструкции.")

        # отправка в ЛС добавившему
        if adder:
            await self._safe_dm(adder, embed)

        # отправка овнеру (если он не тот же человек и не None)
        if owner and (not adder or owner.id != adder.id):
            await self._safe_dm(owner, embed)

    async def _try_get_adder(self, guild: disnake.Guild) -> disnake.Member | None:
        """
        Пытается найти пользователя, добавившего бота, через аудит-лог.
        Требуются права View Audit Log у бота. Возвращает Member или None.
        """
        try:
            if not guild.me.guild_permissions.view_audit_log:
                return None

            # иногда событие пишетcя не мгновенно — попробуем пару попыток
            for _ in range(3):
                async for entry in guild.audit_logs(
                    limit=5,
                    action=disnake.AuditLogAction.bot_add
                ):
                    # target — это добавленный бот; проверяем, что это мы
                    if getattr(entry.target, "id", None) == self.bot.user.id:
                        user = entry.user
                        # вернуть Member (а не User), если возможно
                        if isinstance(user, disnake.Member):
                            return user
                        try:
                            return await guild.fetch_member(user.id)
                        except Exception:
                            return guild.get_member(user.id)
                await asyncio.sleep(1)
        except Exception as e:
            print(f"[GuildJoinNotifier] Не удалось получить аудит-лог на {guild.id}: {e}")
        return None

    async def _safe_dm(self, member: disnake.abc.User, embed: disnake.Embed):
        try:
            await member.send(embed=embed)
        except Exception as e:
            # ЛС закрыты, игнорируем
            print(f"[GuildJoinNotifier] Не удалось отправить ЛС {getattr(member, 'id', '?')}: {e}")


def setup(bot: commands.Bot):
    bot.add_cog(GuildJoinNotifier(bot))
