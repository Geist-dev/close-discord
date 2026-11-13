import disnake
from disnake.ext import commands
from utils.databases import UsersDataBase  # твоя база


class EventHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def manage_event(self, inter: disnake.MessageInteraction, user_id: int, guild_id: int, rl_name: str):
        """Вывод меню управления событием"""
        pot = await UsersDataBase().get_user(user_id)
        kl = pot[0][7]

        # Формат игры (например 5x5 BO3)
        try:
            game_format = f"{kl.split('_')[0]} {kl.split('_')[1]} {kl.split('_')[2]}"
        except IndexError:
            game_format = kl

        embed = disnake.Embed(
            title=f"Управление событием - {inter.user.name}",
            description=f"> Информация о игре\n\nФормат: **{game_format}**",
            color=disnake.Color.blurple(),
        )

        # Аватарка
        if inter.user.avatar:
            embed.set_thumbnail(url=inter.user.avatar.url)
        else:
            embed.set_thumbnail(url=inter.user.default_avatar.url)

        # Кнопки управления
        view = disnake.ui.View(timeout=None)
        view.add_item(
            disnake.ui.Button(
                label="Запустить/завершить событие",
                style=disnake.ButtonStyle.grey,
                custom_id=f"событие_{inter.user.id}_{guild_id}_{rl_name}",
                emoji='🔹',
            )
        )
        view.add_item(
            disnake.ui.Button(
                label="Очистить список игроков",
                style=disnake.ButtonStyle.grey,
                custom_id=f"список_{inter.user.id}_{guild_id}_{rl_name}",
                emoji='🔹',
            )
        )
        view.add_item(
            disnake.ui.Button(
                label="Настроить всё с нуля",
                style=disnake.ButtonStyle.grey,
                custom_id=f"снуля_{inter.user.id}_{guild_id}_{rl_name}",
                emoji='🔹',
            )
        )
        view.add_item(
            disnake.ui.Button(
                label="Поменять игроков местами",
                style=disnake.ButtonStyle.grey,
                custom_id=f"смена_{inter.user.id}_{guild_id}_{rl_name}",
                emoji='🔹',
            )
        )
        view.add_item(
            disnake.ui.Button(
                label="Пинг роли",
                style=disnake.ButtonStyle.grey,
                custom_id=f"пинг_{inter.user.id}_{guild_id}_{rl_name}",
                disabled=True,
                emoji='🔹'
            )
        )

        await inter.send(embed=embed, view=view, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(EventHandler(bot))
