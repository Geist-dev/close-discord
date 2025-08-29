import disnake
from disnake.ext import commands
from utils.databases import UsersDataBase
from cogs.select import SelectGames6  # предполагаю, что SelectGames6 у тебя в ui/selects.py


class Closechange(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def create_close(self, inter: disnake.AppCmdInter, game_name: str):
        await inter.response.defer(with_message=False)

        user_id = inter.author.id
        guild = inter.guild
        stop_players = []

        # Получаем всех игроков
        all_users = await UsersDataBase().get_user_vse(user_id)
        user_data = await UsersDataBase().get_user(user_id)

        for user in all_users:
            if user[1] == user[2]:
                if user[9] == 1:
                    stop_players.append(user[2])
            else:
                stop_players.append(user[2])

        if stop_players:
            view = disnake.ui.View(timeout=None)
            view.add_item(SelectGames6(user_id, guild.id, stop_players, self.bot))

            embed = disnake.Embed(
                title="Выбор игроков для смены",
                description=f"Игра: **{game_name}**",
                color=disnake.Color.blurple(),
            )

            avatar = inter.user.avatar or inter.user.default_avatar
            embed.set_thumbnail(url=avatar)

            await inter.send(embed=embed, view=view, ephemeral=True)
        else:
            await inter.send("Нет доступных игроков.", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Closechange(bot))
