import disnake
from disnake.ext import commands
import datetime
import time
from utils.databases import UsersDataBase  # твой модуль с базой
from .select import SelectGames, SelectGames1

class Closebegin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def process_close(self, inter: disnake.MessageInteraction, user_id: int, guild_id: int, rl_name: str):
        await inter.response.defer(with_message=False)
        guild = self.bot.get_guild(guild_id)

        # Получаем пользователя и список
        user_data = await UsersDataBase().get_user(user_id)
        players = await UsersDataBase().get_user_vse(user_id)

        removed_count = 0
        for player in players:
            if player[1] != player[2]:
                await UsersDataBase().del_user(player[2])
            else:
                await UsersDataBase().update_igr(0, user_id)
                removed_count = player[10]

        # Отображение нормальных названий игр
        pretty_name = {"CS2": "CS2", "DOTA2": "Dota 2", "VALORANT": "Valorant"}.get(rl_name, rl_name)

        embed = disnake.Embed(
            title=f"Управление клозом - {inter.user.name}",
            description="<:__:1211092869276770315> - **подтвердить** настройки данного матча\n<:1_:1208208287598780477> - **отменить** данную игру",
            color=disnake.Color.blurple(),
        )

        # аватарка
        if inter.user.avatar is None:
            embed.set_thumbnail(url=inter.user.default_avatar.url)
        else:
            embed.set_thumbnail(url=inter.user.avatar.url)

        # UI элементы
        view = disnake.ui.View(timeout=None)
        view.add_item(SelectGames(inter.user.id, rl_name, inter.guild.id, self.bot))
        if rl_name not in "DOTA2":
            view.add_item(SelectGames1(inter.user.id, inter.guild.id, self.bot))
        view.add_item(disnake.ui.Button(label="Подтвердить", style=disnake.ButtonStyle.grey,
                                        custom_id=f"подтвердить_{inter.user.id}_{guild_id}_{rl_name}",
                                        emoji='<:__:1211092869276770315>'))
        view.add_item(disnake.ui.Button(label="Удалить матч", style=disnake.ButtonStyle.grey,
                                        custom_id=f"удалить_{inter.user.id}_{guild_id}",
                                        emoji='<:1_:1208208287598780477>'))

        # Обновление сообщения
        try:
            channel = inter.channel
            msg = channel.get_partial_message(user_data[0][6])
            await msg.edit(embed=embed, view=view)
        except Exception as e:
            print(f"Ошибка при обновлении сообщения: {e}")

        # Ограничение прав доступа для игроков
        try:
            match_channel = self.bot.get_channel(user_data[0][4])
            old_message = match_channel.get_partial_message(user_data[0][13])
            msg = match_channel.get_partial_message(user_data[0][19])

            overwrite = disnake.PermissionOverwrite(view_channel=None)
            for player in players:
                if player[1] != player[2]:
                    target = guild.get_member(player[2]) or await guild.fetch_member(player[2])
                    if target:
                        await match_channel.set_permissions(target, overwrite=overwrite)

            # ограничения для роли
            conf = await UsersDataBase().get_config_by_guild(inter.guild.id)
            role_evri = guild.get_role(conf["role_id_evri"])
            if role_evri:
                deny = disnake.PermissionOverwrite(
                    view_channel=None,
                    mention_everyone=False,
                    send_messages=False,
                    attach_files=False,
                    add_reactions=False,
                    manage_messages=False,
                    embed_links=False,
                )
                await match_channel.set_permissions(role_evri, overwrite=deny)
            await old_message.delete()
            await msg.delete()

        except Exception as e:
            print(f"Ошибка при ограничении доступа: {e}")

        # Удаляем временные каналы, если они были
        for idx in [16, 17, 19]:
            ch_id = user_data[0][idx]
            if ch_id != 0:
                ch = self.bot.get_channel(ch_id)
                if ch:
                    await ch.delete()

        # Сброс параметров в БД
        await UsersDataBase().update_kol(0 - removed_count, user_id)
        await UsersDataBase().update_format("нет", user_id)
        await UsersDataBase().update_tip(0, user_id)
        await UsersDataBase().update_rl_name(0, user_id)
        await UsersDataBase().update_team(0, user_id)
        await UsersDataBase().update_messeg2(0, user_id)
        await UsersDataBase().update_kap(0, user_id)
        await UsersDataBase().update_kap1(1 - user_data[0][15], user_id)
        await UsersDataBase().update_channel3(0, user_id)
        await UsersDataBase().update_channel4(0, user_id)


def setup(bot: commands.Bot):
    bot.add_cog(Closebegin(bot))
