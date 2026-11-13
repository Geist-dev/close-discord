import disnake
from disnake.ext import commands
from utils.databases import UsersDataBase
from disnake.utils import get
from disnake.ui import View

from .select import SelectGames, SelectGames1

class PlayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_close(self, inter: disnake.MessageInteraction, rl_name: str):
        await inter.response.defer(with_message=False)
        await inter.edit_original_response(components=None)

        trax = await UsersDataBase().get_user(inter.user.id)
        if trax != []:
            await inter.send('Вы уже участвуйте в Close!', ephemeral=True)
            return

        conf2 = await UsersDataBase().get_config_by_guild(inter.guild.id)
        if not conf2:
            await inter.send('Сначала настройте бота командой /config.', ephemeral=True)
            return
        guild_id = inter.guild.id
        guild = self.bot.get_guild(guild_id)

        role_evri = guild.default_role
        role_closeban = guild.get_role(int(conf2['closeban_id']))
        role_closemod = guild.get_role(int(conf2['role_closemod_id']))
        role_otvechclosemod = guild.get_role(int(conf2['role_otvechclosemod_id']))

        target = guild.get_member(inter.user.id) or await guild.fetch_member(inter.user.id)

        defer_cat = get(guild.categories, id=int(conf2['categori_pod_id']))

        if defer_cat is None:
            await inter.send('Настроенная категория не найдена. Обновите /config.', ephemeral=True)
            return

        # Формируем словари с overwrite-правами для каждого канала
        overwrites_fred = {
            target: disnake.PermissionOverwrite(view_channel=True, mention_everyone=False, send_messages=True),
            role_otvechclosemod: disnake.PermissionOverwrite(view_channel=True, mention_everyone=False, send_messages=True),
            role_evri: disnake.PermissionOverwrite(view_channel=False, mention_everyone=False)
        }

        overwrites_fred1 = {
            role_evri: disnake.PermissionOverwrite(
                mention_everyone=False,
                send_messages=False,
                attach_files=False,
                add_reactions=False,
                manage_messages=False,
                embed_links=False
            ),
            target: disnake.PermissionOverwrite(send_messages=True, manage_messages=True)
        }

        overwrites_fred2 = {
            target: disnake.PermissionOverwrite(view_channel=True, connect=True, send_messages=True, manage_messages=False),
            role_evri: disnake.PermissionOverwrite(
                mention_everyone=False,
                stream=True,
                change_nickname=False,
                use_embedded_activities=False,
                send_messages=False,
                attach_files=False,
                add_reactions=False,
                manage_messages=False,
                embed_links=False
            ),
            role_closeban: disnake.PermissionOverwrite(view_channel=False, mention_everyone=False),
            role_closemod: disnake.PermissionOverwrite(view_channel=True, connect=True, manage_messages=False, manage_nicknames=True, mute_members=True, move_members=True)
        }

        overwrites_fred = {role: permissions for role, permissions in overwrites_fred.items() if role is not None}
        overwrites_fred2 = {role: permissions for role, permissions in overwrites_fred2.items() if role is not None}

        # Создаём категорию
        category = await guild.create_category(f"CLOSE {rl_name} ・ {inter.user.name}", position=defer_cat.position)

        # Создаём каналы с нужными правами сразу
        fred = await guild.create_text_channel("🛠・управление", category=category, overwrites=overwrites_fred)
        fred1 = await guild.create_text_channel("💬・запись", category=category, overwrites=overwrites_fred1)
        fred2 = await guild.create_voice_channel(f"🎮・{inter.component.custom_id}・ {inter.user.name}", category=category, overwrites=overwrites_fred2)

        embed = disnake.Embed(
            title=f"Управление клозом - {inter.user.name}",
            description=f"• - **подтвердить** настройки данного матча\n• - **отменить** данную игру"
        )
        embed.set_thumbnail(url=inter.user.avatar or inter.user.default_avatar)

        v = View(timeout=None)
        hp = inter.user.id
        v.add_item(SelectGames(hp, rl_name, inter.guild.id, self.bot))
        if rl_name != "DOTA2":
            v.add_item(SelectGames1(hp, inter.guild.id, self.bot))

        but = disnake.ui.Button(
            label="Подтвердить",
            style=disnake.ButtonStyle.grey,
            custom_id=f"подтвердить_{inter.user.id}_{guild_id}_{inter.component.custom_id}",
            emoji='🔹'
        )
        v.add_item(but)

        v.add_item(disnake.ui.Button(
            label="Удалить матч",
            style=disnake.ButtonStyle.grey,
            custom_id=f"удалить_{inter.user.id}_{guild_id}",
            emoji='🔹'
        ))

        tru = await fred.send(embed=embed, view=v)
        await UsersDataBase().add_user(inter.user.id, inter.user.id, fred.id, fred1.id, fred2.id, tru.id, inter.guild.id)

        await inter.send(f'Вы создали Close\n\nПерейдите в канал <#{fred2.id}>', ephemeral=True)


def setup(bot):
    bot.add_cog(PlayCog(bot))
