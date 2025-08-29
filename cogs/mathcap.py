import disnake
from disnake.ext import commands
from disnake.ui import TextInput
from disnake import TextInputStyle
from utils.databases import UsersDataBase
from .select import SelectGames2

class Matchcap(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def create_close(self, inter: disnake.AppCmdInter, rl_name: str):
        """Основная логика старта матча"""
        guild_id = inter.guild.id
        user_id = inter.user.id
        guild = self.bot.get_guild(guild_id)

        hp = await UsersDataBase().get_user(user_id)
        if not hp:
            return await inter.send("❌ Не найден пользователь в базе данных.", ephemeral=True)

        # Проверка количества игроков
        expected_players = int(hp[0][7].split('_')[1][0]) * 2
        if hp[0][10] != expected_players:
            return await inter.send(f"Нет **{expected_players}** человек для игры!", ephemeral=True)

        # Загружаем всех игроков
        players = await UsersDataBase().get_user_vse(user_id)

        stop = []
        trep1, trep2, g = None, None, 0

        for i in players:
            stop.append(i[2])
            if i[14] == 1:
                g += 1
                trep1 = i[2]
            elif i[14] == 2:
                g += 1
                trep2 = i[2]

        # Если капитанов нет → предлагаем выбрать
        if g != 2:
            embed = disnake.Embed(
                title=f"Управление матчем - {inter.user.name}",
                description=f"Выберите капитанов",
                color=disnake.Color.blurple()
            )
            avatar = inter.user.display_avatar.url
            embed.set_thumbnail(url=avatar)

            view = disnake.ui.View(timeout=None)
            view.add_item(SelectGames2(inter.user.id, guild.id, stop, self.bot))  # ← твой селект

            return await inter.send(embed=embed, view=view, ephemeral=True)

        # Если капитаны есть → запускаем модалку
        modal = self.MatchDataModal(self.bot, guild_id, user_id, hp, trep1, trep2, rl_name)
        await inter.response.send_modal(modal=modal)

    # ---------------- МОДАЛКА ----------------
    class MatchDataModal(disnake.ui.Modal):
        def __init__(self, bot, guild_id, user_id, hp, trep1, trep2, rl_name):
            self.bot = bot
            self.guild_id = guild_id
            self.user_id = user_id
            self.hp = hp
            self.trep1 = trep1
            self.trep2 = trep2
            self.rl_name = rl_name

            components = [
                TextInput(
                    label="Данные для игры",
                    placeholder="Введите ссылку на лобби, пароль и т.п.",
                    custom_id="match_data",
                    style=TextInputStyle.paragraph,
                )
            ]
            super().__init__(title="Укажите данные для игры", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            await inter.response.defer(with_message=False)

            guild = self.bot.get_guild(self.guild_id)
            channel = self.bot.get_channel(self.hp[0][4])
            match_msg = channel.get_partial_message(self.hp[0][13])

            # Создаем embed с инфой
            embed = disnake.Embed(
                title="Игра началась",
                description="**Заходите в комнаты своих команд после выбора капитанов.**\n"
                            "*P.S. не забудьте прочитать правила*"
            )
            for key, value in inter.text_values.items():
                embed.add_field(name=key, value=f"```\n{value[:1024]}```", inline=False)

            # Разрешения для игроков
            players = await UsersDataBase().get_user_vse(self.user_id)
            for i in players:
                member = guild.get_member(i[2]) or await guild.fetch_member(i[2])
                overwrite = disnake.PermissionOverwrite(view_channel=True)
                await channel.set_permissions(member, overwrite=overwrite)

            # Обновляем сообщение
            await match_msg.edit(embed=embed, components=[
                disnake.ui.Button(
                    label="Выберите игрока в свою команду",
                    style=disnake.ButtonStyle.green,
                    custom_id=f"выбор_{inter.user.id}_{self.guild_id}_{self.rl_name}"
                )
            ])

            # Тут же создаём голосовые каналы и выдаём права
            await self._create_voice_channels(inter, guild, channel)

        async def _create_voice_channels(self, inter, guild, text_channel):
            """Создание голосовых каналов и настройка прав"""
            rl_name = self.rl_name
            trep1, trep2 = self.trep1, self.trep2
            hp = self.hp

            if rl_name == 'DOTA2':
                av, bv = '🅰️ The Radiant', '🅱️ The Dire'
            else:
                av, bv = '🅰️ Team A', '🅱️ Team B'

            main_channel = guild.get_channel(hp[0][4])
            category = main_channel.category

            vc1 = await guild.create_voice_channel(av, category=category)
            vc2 = await guild.create_voice_channel(bv, category=category)

            await UsersDataBase().update_channel3(vc1.id, self.user_id)
            await UsersDataBase().update_channel4(vc2.id, self.user_id)

            conf = await UsersDataBase().get_config_by_guild(inter.guild.id)
            role_evri = guild.get_role(int(conf['role_id_evri']))
            role_closeban = guild.get_role(int(conf['closeban_id']))
            role_closemod = guild.get_role(int(conf['role_closemod_id']))
            captain1 = guild.get_member(trep1) or await guild.fetch_member(trep1)
            captain2 = guild.get_member(trep2) or await guild.fetch_member(trep2)
            moderator = guild.get_member(inter.user.id) or await guild.fetch_member(inter.user.id)

            # Доступ RL
            await vc1.set_permissions(moderator, view_channel=True, connect=True)
            await vc2.set_permissions(moderator, view_channel=True, connect=True)

            # Запрещаем доступ всем
            await vc1.set_permissions(role_evri, connect=False)
            await vc2.set_permissions(role_evri, connect=False)

            # Бан роль
            await vc1.set_permissions(role_closeban, view_channel=False)
            await vc2.set_permissions(role_closeban, view_channel=False)

            # Модераторам
            await vc1.set_permissions(role_closemod, view_channel=True, connect=True, mute_members=True,
                                          move_members=True)
            await vc2.set_permissions(role_closemod, view_channel=True, connect=True, mute_members=True,
                                          move_members=True)

            # Доступ капитанов
            await vc1.set_permissions(captain1, view_channel=True, connect=True)
            await vc2.set_permissions(captain2, view_channel=True, connect=True)

            embed = disnake.Embed(
                title="Капитаны",
                description=f"🅰️ <@{captain1.id}>\n\n🅱️ <@{captain2.id}>"
            )
            result_msg = await text_channel.send(embed=embed)
            await UsersDataBase().update_messeg3(result_msg.id, self.user_id)

def setup(bot: commands.Bot):
    bot.add_cog(Matchcap(bot))
