# cogs/ping_handler.py
import time
import disnake
from disnake.ext import commands
from utils.databases import UsersDataBase



class PingHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def process_ping(self, inter: disnake.AppCmdInter, user_id: int, guild_id: int, rl_name: str):
        """Пинг роли с ограничением раз в 10 минут"""

        await inter.response.defer(with_message=False)

        # Получаем данные пользователя
        user_data = await UsersDataBase().get_user(user_id)
        if not user_data:
            await inter.send("❌ Пользователь не найден в базе", ephemeral=True)
            return

        user_data = user_data[0]  # вытаскиваем первую строку

        # Проверка кулдауна (индекс 21 — время до которого нельзя пинговать)
        cooldown_time = user_data[21]
        if cooldown_time and cooldown_time > time.time():
            await inter.send("⏳ Пинговать можно раз в 10 минут", ephemeral=True)
            return

        # Обновляем кулдаун
        await UsersDataBase().update_ping(time.time() + (10 * 60), user_id)

        # Получаем канал
        channel = self.bot.get_channel(user_data[4])
        if not channel:
            await inter.send("❌ Канал не найден", ephemeral=True)
            return

        # Исправляем имя роли, если это LoL
        role_key = "bravlhel" if rl_name == "LoL" else rl_name

        # Формируем сообщение
        conf = await UsersDataBase().get_config_by_guild(inter.guild.id)
        try:
            # остаток мест (индекс 7 — видимо "mode_x", индекс 10 — текущее число участников)
            max_players = int(user_data[7].split("_")[1][0]) * 2
            current_players = user_data[10]
            remaining = max_players - current_players
            await channel.send(f'<@&{conf[role_key]}> +**{remaining}**')
        except Exception:
            await channel.send(f'<@&{conf[role_key]}> заходи')

        await inter.send("✅ Вы пинганули роль", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(PingHandler(bot))
