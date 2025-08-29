import disnake
from disnake.ext import commands
import datetime, time
from utils.databases import UsersDataBase


class EventCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def toggle_event(self, inter: disnake.MessageInteraction, user_id: int, guild_id: int, rl_name: str):
        """Создание или завершение события"""
        await inter.response.defer(with_message=False)

        guild = self.bot.get_guild(guild_id)
        if guild is None:
            await inter.send("❌ Сервер не найден.", ephemeral=True)
            return

        try:
            # Попытка создать событие
            pot = await UsersDataBase().get_user(user_id)
            if not pot:
                await inter.send("❌ Пользователь не найден в базе.", ephemeral=True)
                return

            channel = self.bot.get_channel(pot[0][5])
            if channel is None:
                await inter.send("❌ Канал для события не найден.", ephemeral=True)
                return

            ff = await guild.create_scheduled_event(
                name=f"🎥・{rl_name}・{inter.user.name}",
                scheduled_start_time=datetime.datetime.fromtimestamp(time.time() + 60),
                channel=channel,
            )
            await ff.start()

            # Сохраняем ID события в БД
            await UsersDataBase().update_event_id(ff.id, user_id)

            await inter.send("✅ Вы создали событие.", ephemeral=True)

        except Exception:
            # Если событие уже есть → удаляем
            hh = await UsersDataBase().get_user(user_id)
            if not hh or not hh[0][18]:
                await inter.send("❌ Не удалось завершить событие.", ephemeral=True)
                return

            ff = guild.get_scheduled_event(hh[0][18])
            if ff:
                await ff.delete()
                await inter.send("🛑 Вы завершили событие.", ephemeral=True)
            else:
                await inter.send("⚠ Событие уже удалено.", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(EventCog(bot))
