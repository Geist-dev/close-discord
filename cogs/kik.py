# cogs/select_player.py
import disnake
from disnake.ext import commands
from utils.databases import UsersDataBase
from cogs.select import SelectGames4  # Ваш компонент выбора игроков


class SelectPlayerCog(commands.Cog):
    """Ког для выбора игроков в матчах"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def open_player_selector(self, inter: disnake.MessageInteraction, user_id: int, guild_id: int, rl_name: str):
        """Открывает модалку/вью для выбора игрока"""
        await inter.response.defer(with_message=False)
        guild = self.bot.get_guild(guild_id)
        if not guild:
            await inter.send("❌ Сервер не найден", ephemeral=True)
            return

        gt = await UsersDataBase().get_user_vse(user_id)
        fr = await UsersDataBase().get_user(user_id)
        rt = await UsersDataBase().get_user(inter.user.id)

        stop = [i[2] for i in gt if i[1] != i[2]]

        if not stop:
            await inter.send("Никого нет из игроков", ephemeral=True)
            return

        # Создаем View с вашим компонентом выбора
        v = disnake.ui.View(timeout=None)
        conf = await UsersDataBase().get_config_by_guild(inter.guild.id)
        v.add_item(SelectGames4(user_id, guild.id, stop, rl_name, self.bot))

        embed = disnake.Embed(
            title="Выбор игрока",
            description="Выберите игрока из списка",
            color=disnake.Color.blurple()
        )

        # Аватар пользователя
        embed.set_thumbnail(url=inter.user.avatar or inter.user.default_avatar)

        await inter.send(embed=embed, view=v, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(SelectPlayerCog(bot))
