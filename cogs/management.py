import disnake
from disnake.ext import commands
from utils.databases import UsersDataBase


class EventManagerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def open_event_manager(self, inter: disnake.MessageInteraction, user_id: int, guild_id: int, rl_name: str):
        await inter.response.defer(with_message=False)

        pot = await UsersDataBase().get_user(user_id)
        if not pot:
            await inter.send("❌ Пользователь не найден в базе данных.", ephemeral=True)
            return

        kl = pot[0][7]  # формат игры

        embed = disnake.Embed(
            title=f"Управление событием - {inter.user.name}",
            description=f"> Информация об игре\n\nФормат: **{' '.join(kl.split('_')[:3])}**",
            color=disnake.Color.blurple(),
        )

        # Миниатюра (аватарка пользователя)
        avatar_url = (
            inter.user.avatar.url if inter.user.avatar else inter.user.default_avatar.url
        )
        embed.set_thumbnail(url=avatar_url)

        # Кнопки управления
        view = disnake.ui.ActionRow(
            disnake.ui.Button(
                label="Запустить/завершить событие",
                style=disnake.ButtonStyle.grey,
                custom_id=f"событие_{inter.user.id}_{guild_id}_{rl_name}",
                emoji="<:3_:1208208490745827338>",
            ),
        )

        view2 = disnake.ui.ActionRow(
            disnake.ui.Button(
                label="Очистить список игроков",
                style=disnake.ButtonStyle.grey,
                custom_id=f"список_{inter.user.id}_{guild_id}_{rl_name}",
                emoji="<:clear:1410716505879871608>",
            ),
            disnake.ui.Button(
                label="Настроить всё с нуля",
                style=disnake.ButtonStyle.grey,
                custom_id=f"снуля_{inter.user.id}_{guild_id}_{rl_name}",
                emoji="<:refresh:1410714424620355716>",
            ),
        )

        view3 = disnake.ui.ActionRow(
            disnake.ui.Button(
                label="Поменять игроков местами",
                style=disnake.ButtonStyle.grey,
                custom_id=f"смена_{inter.user.id}_{guild_id}_{rl_name}",
                disabled=True,
                emoji="<:swap:1410714485911588938>",
            ),
            disnake.ui.Button(
                label="Пинг роли",
                style=disnake.ButtonStyle.grey,
                custom_id=f"пинг_{inter.user.id}_{guild_id}_{rl_name}",
                emoji='<:__:1208208236075819008>'
            ),
        )

        await inter.send(embed=embed, components=[view, view2, view3], ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(EventManagerCog(bot))
