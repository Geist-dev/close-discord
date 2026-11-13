import random
import disnake
from disnake.ext import commands
from disnake.ui import Modal, TextInput, Button
from disnake.enums import TextInputStyle
from utils.databases import UsersDataBase






class MatchHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class GameDataModal(Modal):
        """Модальное окно для ввода данных игры"""
        def __init__(self, handler, hp, channel_id, message_id, user_id, guild_id, rl_name):
            self.handler = handler
            self.hp = hp
            self.channel_id = channel_id
            self.message_id = message_id
            self.user_id = user_id
            self.guild_id = guild_id
            self.rl_name = rl_name

            components = [
                TextInput(
                    label="Данные для игры",
                    placeholder="Введите правила или описание",
                    custom_id="game_data",
                    style=TextInputStyle.paragraph,
                )
            ]
            super().__init__(title="Укажите данные для игры", components=components)

        async def callback(self, inter: disnake.ModalInteraction):
            await inter.response.defer(with_message=False)
            await self.handler.start_match(
                inter, self.hp, self.channel_id, self.message_id,
                self.user_id, self.guild_id, self.rl_name
            )

    async def open_modal(self, inter: disnake.AppCmdInter, user_id: int, guild_id: int, rl_name: str):
        """Открывает модалку если игроков достаточно"""
        hp = await UsersDataBase().get_user(user_id)
        required_players = int(hp[0][7].split('_')[1][0]) * 2

        if hp[0][10] != required_players:
            await inter.send(f"Нет **{required_players}** человек для игры!", ephemeral=True)
            return

        modal = self.GameDataModal(self, hp, hp[0][4], hp[0][13], user_id, guild_id, rl_name)
        await inter.response.send_modal(modal=modal)

    async def start_match(self, inter, hp, channel_id, message_id, user_id, guild_id, rl_name):
        """Основная логика запуска матча"""

        # --- Обновляем сообщение с игрой
        embed = disnake.Embed(
            title="Игра началась",
            description="**Заходите в свои команды и присоединяйтесь к игре.**\n"
                        "*P.S. не забудьте прочитать правила*"
        )
        for key, value in inter.text_values.items():
            embed.add_field(name="Данные для игры", value=f"```\n{value[:1024]}```", inline=False)

        channel = self.bot.get_channel(channel_id)
        msg = channel.get_partial_message(message_id)
        await msg.edit(embed=embed, components=None)

        # --- Панель управления матчем
        format_info = hp[0][7]
        manage_embed = disnake.Embed(
            title=f"Управление матчем - {inter.user.name}",
            description=f"Формат: **{format_info.split('_')[0]} {format_info.split('_')[1]}**\nТип матча: **Миксы**"
        )
        avatar = inter.user.avatar or inter.user.default_avatar
        manage_embed.set_thumbnail(url=avatar)

        manage_buttons = [[
            Button(label="Начать матч", style=disnake.ButtonStyle.grey,
                   custom_id=f"Миксы_{inter.user.id}_{guild_id}_{rl_name}",
                   disabled=True, emoji='🔹'),
            Button(label="Кикнуть", style=disnake.ButtonStyle.grey,
                   custom_id=f"кикнуть_{inter.user.id}_{guild_id}_{rl_name}",
                   emoji='🔹'),
            Button(label="Забанить", style=disnake.ButtonStyle.grey,
                   custom_id=f"Closeban_100_{guild_id}",
                   emoji='🔹')],
            [Button(label="Управление", style=disnake.ButtonStyle.grey,
                   custom_id=f"руслан_{inter.user.id}_{guild_id}_{rl_name}",
                   emoji='🔹'),
            Button(label="Удалить матч", style=disnake.ButtonStyle.grey,
                   custom_id=f"удалить_{inter.user.id}_{guild_id}",
                   emoji='🔹')
        ]]
        await inter.edit_original_response(embed=manage_embed, components=manage_buttons)

        # --- Названия команд
        if rl_name == "DOTA2":
            team_a, team_b = "🅰️ The Radiant", "🅱️ The Dire"
        else:
            team_a, team_b = "🅰️ Team A", "🅱️ Team B"

        guild = self.bot.get_guild(guild_id)
        base_channel = guild.get_channel(hp[0][4])
        conf = base_channel.category.id
        category = disnake.utils.get(guild.categories, id=conf)

        # Создаем 2 голосовых канала
        voice_a = await guild.create_voice_channel(team_a, category=category)
        voice_b = await guild.create_voice_channel(team_b, category=category)

        await UsersDataBase().update_channel3(voice_a.id, user_id)
        await UsersDataBase().update_channel4(voice_b.id, user_id)

        # --- Роли
        conf = await UsersDataBase().get_config_by_guild(inter.guild.id)
        role_evri = guild.get_role(int(conf['role_id_evri']))
        role_closeban = guild.get_role(int(conf['closeban_id']))
        role_closemod = guild.get_role(int(conf['role_closemod_id']))
        moderator = guild.get_member(inter.user.id) or await guild.fetch_member(inter.user.id)

        # Доступ RL
        await voice_a.set_permissions(moderator, view_channel=True, connect=True)
        await voice_b.set_permissions(moderator, view_channel=True, connect=True)

        # Запрещаем доступ всем
        await voice_a.set_permissions(role_evri, connect=False)
        await voice_b.set_permissions(role_evri, connect=False)

        # Бан роль
        await voice_a.set_permissions(role_closeban, view_channel=False)
        await voice_b.set_permissions(role_closeban, view_channel=False)

        # Модераторам
        await voice_a.set_permissions(role_closemod, view_channel=True, connect=True, mute_members=True, move_members=True)
        await voice_b.set_permissions(role_closemod, view_channel=True, connect=True, mute_members=True, move_members=True)

        # --- Распределение игроков
        players = await UsersDataBase().get_user_vse(user_id)
        team1, team2 = await self.distribute_players(guild, players, rl_name, voice_a, voice_b, base_channel, user_id)

        # --- Отправка эмбеда с составами
        embed = disnake.Embed(title="Команды", description=f"{team1}\n\n{team2}")
        result_msg = await channel.send(embed=embed)
        await UsersDataBase().update_messeg3(result_msg.id, user_id)

        await inter.send("Игра началась ✅", ephemeral=True)

    async def distribute_players(self, guild, players, rl_name, voice_a, voice_b, base_channel, user_id):
        """Распределяет игроков по командам"""
        team1, team2 = "", ""
        k = []

        if rl_name not in "DOTA2":
            # --- Случайные миксы
            hp = await UsersDataBase().get_user(user_id)
            for _ in range(int(hp[0][7].split('_')[1][0])):
                k.append(1)
                k.append(2)

            for p in players:
                if p[1] != p[2]:
                    side = random.choice(k)
                    await UsersDataBase().update_team(side, p[2])
                    await self.move_player(guild, p[2], side, voice_a, voice_b, base_channel)
                    k.remove(side)
                else:
                    if p[9] == 1 and k:
                        side = random.choice(k)
                        await UsersDataBase().update_team(side, p[2])
                        k.remove(side)
                    await base_channel.set_permissions(guild.get_member(p[2]), view_channel=True, send_messages=True)

        else:
            # --- Для Dota2: распределяем по позициям
            for j in range(5):
                side = random.randint(1, 2)
                for p in players:
                    if p[11] == j + 1:
                        if p[1] != p[2]:
                            await UsersDataBase().update_team(side, p[2])
                            await self.move_player(guild, p[2], side, voice_a, voice_b, base_channel)
                            side = 2 if side == 1 else 1
                        else:
                            if p[9] == 1:
                                await UsersDataBase().update_team(side, p[2])
                                side = 2 if side == 1 else 1
                            await base_channel.set_permissions(guild.get_member(p[2]), view_channel=True, send_messages=True)

        # --- Формируем эмбед команд
        for p in await UsersDataBase().get_user_vse(user_id):

            role_name = self.get_role_name(p[11], rl_name)
            member_str = f"{role_name}\n<@!{p[2]}> ({p[2]})\n\n"

            if p[12] == 1:
                team1 += member_str
            elif p[12] == 2:
                team2 += member_str

        return f"{voice_a.name}\n{team1}", f"{voice_b.name}\n{team2}"

    async def move_player(self, guild, user_id, side, voice_a, voice_b, base_channel):
        """Перемещает игрока в команду"""
        member = guild.get_member(user_id) or await guild.fetch_member(user_id)
        if side == 1:
            if member.voice:
                await member.move_to(voice_a)
            await voice_a.set_permissions(member, view_channel=True, connect=True)
        else:
            if member.voice:
                await member.move_to(voice_b)
            await voice_b.set_permissions(member, view_channel=True, connect=True)
        await base_channel.set_permissions(member, view_channel=True)

    def get_role_name(self, pos, rl_name):
        roles = {
            1: "1️⃣ Керри",
            2: "2️⃣ Мидер",
            3: "3️⃣ Хард/Офлейн",
            4: "4️⃣ Поддержка",
            5: "5️⃣ Полная поддержка",
        }
        return roles.get(pos, "")


def setup(bot: commands.Bot):
    bot.add_cog(MatchHandler(bot))
