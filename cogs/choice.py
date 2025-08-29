import disnake
from disnake.ext import commands
from utils.databases import UsersDataBase
from cogs.select import SelectGames3  # твой селект выбора игроков


class ChoiceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def choice_close(self, inter: disnake.MessageInteraction, user_id: int):
        await inter.response.defer(with_message=False)

        # Данные игроков
        gt = await UsersDataBase().get_user_vse(user_id)
        fr = await UsersDataBase().get_user(user_id)
        rt = await UsersDataBase().get_user(inter.user.id)

        # Проверка что игрок не выбрал уже максимум
        if fr[0][15] != ((int(fr[0][7].split('_')[1][0]) * 2) - 1):
            # Проверка что это капитан
            if rt[0][14] != 0:
                # Проверка что ходит именно этот капитан
                if fr[0][15] % 2 + 1 == rt[0][14]:
                    stop = []

                    # Формируем список доступных игроков
                    for i in gt:
                        if i[14] not in (1, 2) and i[12] == 0:
                            if i[1] == i[2]:
                                if i[9] == 1:
                                    stop.append(i[2])
                            else:
                                stop.append(i[2])

                    if stop:
                        v = disnake.ui.View(timeout=None)
                        v.add_item(SelectGames3(user_id, inter.guild.id, stop, self.bot))

                        embed = disnake.Embed(
                            title="Выбор игрока",
                            description="Капитан выбирает следующего игрока",
                            color=disnake.Color.blurple(),
                        )

                        # Добавляем аватар в embed
                        avatar_url = (
                            inter.user.avatar.url
                            if inter.user.avatar
                            else inter.user.default_avatar.url
                        )
                        embed.set_thumbnail(url=avatar_url)

                        await inter.send(embed=embed, view=v, ephemeral=True)
                    else:
                        await inter.send(
                            "Уже максимальное количество выбранных игроков",
                            ephemeral=True
                        )
                else:
                    await inter.send("Сейчас выбирает другой капитан", ephemeral=True)
            else:
                await inter.send("Вы не являетесь капитаном", ephemeral=True)
        else:
            await inter.send("Уже максимальное количество выбранных игроков", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(ChoiceCog(bot))
