import disnake
from disnake.ext import commands
from utils.databases import UsersDataBase  # импорт твоей БД

class SelectGames(disnake.ui.Select):
    def __init__(self, ved_id: int, name: str, guild_serv: int, bot: commands.Bot):
        self.ved_id = ved_id
        self.name = name
        self.guild_serv = guild_serv
        self.bot = bot

        # Описание форматов
        formats = [
            ("5x5 Classic", "5x5_classic"),
            ("5x5 Short", "5x5_short"),
            ("4x4 Classic", "4x4_classic"),
            ("4x4 Short", "4x4_short"),
            ("3x3 Classic", "3x3_classic"),
            ("3x3 Short", "3x3_short"),
            ("2x2 Classic", "2x2_classic"),
            ("2x2 Short", "2x2_short"),
            ("1x1 Classic", "1x1_classic"),
            ("1x1 Short", "1x1_short"),
        ]

        options = [
            disnake.SelectOption(label=label, value=f"{self.name}_{value}")
            for label, value in formats
        ]

        super().__init__(
            placeholder="Выберите формат матча",
            options=options,
            custom_id="games",
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer(with_message=False)

        if not interaction.values:
            return await interaction.send("❌ Выберите хотя бы один формат.", ephemeral=True)

        selected_value = interaction.values[0]
        parts = selected_value.split('_', maxsplit=3)
        if len(parts) < 3:
            return await interaction.send("⚠ Ошибка формата данных.", ephemeral=True)

        game_format = "_".join(parts)  # убираем имя ведущего из value

        if interaction.user.id != self.ved_id:
            return await interaction.send("⛔ Вы не являетесь ведущим.", ephemeral=True)

        guild = self.bot.get_guild(self.guild_serv)
        if guild is None:
            return await interaction.send("⚠ Сервер не найден.", ephemeral=True)

        await UsersDataBase().update_format(game_format, self.ved_id)
        await interaction.send(f"✅ Формат матча изменён на **{game_format}**", ephemeral=True)

class SelectGames1(disnake.ui.Select):
    def __init__(self, ved_id: int, guild_serv: int, bot: commands.Bot):
        self.ved_id = ved_id
        self.guild_serv = guild_serv
        self.bot = bot

        options = [
            disnake.SelectOption(label="Микс", value="1"),
            disnake.SelectOption(label="Капитаны", value="2"),
        ]

        super().__init__(
            placeholder="Выберите тип распределения",
            options=options,
            custom_id="games1",
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer(with_message=False)

        if not interaction.values:
            return await interaction.send("❌ Выберите хотя бы один вариант.", ephemeral=True)

        try:
            val = int(interaction.values[0])
        except ValueError:
            return await interaction.send("⚠ Ошибка: некорректное значение.", ephemeral=True)

        if interaction.user.id != self.ved_id:
            return await interaction.send("⛔ Вы не являетесь ведущим.", ephemeral=True)

        guild = self.bot.get_guild(self.guild_serv)
        if guild is None:
            return await interaction.send("⚠ Сервер не найден.", ephemeral=True)

        await UsersDataBase().update_tip(val, self.ved_id)
        await interaction.send(f"✅ Тип распределения изменён на **{'Микс' if val == 1 else 'Капитаны'}**", ephemeral=True)


class SelectGames2(disnake.ui.Select):
    def __init__(self, ved_id: int, guild_serv: int, stop: list[int], bot: commands.Bot):
        self.ved_id = ved_id
        self.guild_serv = guild_serv
        self.stop = stop
        self.bot = bot

        guild = self.bot.get_guild(self.guild_serv)
        options = []

        if guild:
            for member_id in self.stop:
                member = guild.get_member(member_id)
                if member:  # проверка, что участник найден
                    options.append(disnake.SelectOption(
                        label=member.display_name,
                        value=str(member_id)
                    ))

        # если список пуст — подстраховка
        if not options:
            options.append(disnake.SelectOption(label="Нет доступных игроков", value="0"))

        super().__init__(
            placeholder="Выберите капитанов",
            options=options,
            custom_id="games2",
            min_values=2,
            max_values=2
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer(with_message=False)

        if interaction.user.id != self.ved_id:
            return await interaction.send("⛔ Вы не являетесь ведущим.", ephemeral=True)

        if len(interaction.values) != 2 or "0" in interaction.values:
            return await interaction.send("⚠ Нужно выбрать двух капитанов.", ephemeral=True)

        try:
            captain1_id = int(interaction.values[0])
            captain2_id = int(interaction.values[1])
        except ValueError:
            return await interaction.send("⚠ Ошибка: некорректные данные выбора.", ephemeral=True)

        # Обновляем базу
        fd = await UsersDataBase().get_user_vse(self.ved_id)
        for row in fd:
            await UsersDataBase().update_kap(0, row[2])

        await UsersDataBase().update_kap(1, captain1_id)
        await UsersDataBase().update_team(1, captain1_id)

        await UsersDataBase().update_kap(2, captain2_id)
        await UsersDataBase().update_team(2, captain2_id)

        # Убираем меню после выбора
        await interaction.edit_original_response(view=None)

class SelectGames3(disnake.ui.Select):
    def __init__(self, ved_id: int, guild_serv: int, stop: list[int], bot: commands.Bot):
        self.ved_id = ved_id
        self.guild_serv = guild_serv
        self.stop = stop
        self.bot = bot

        guild = self.bot.get_guild(self.guild_serv)
        options = []

        if guild:
            for member_id in self.stop:
                member = guild.get_member(member_id)
                if member:
                    options.append(disnake.SelectOption(
                        label=member.display_name,
                        value=str(member_id)
                    ))

        if not options:
            options.append(disnake.SelectOption(label="Нет доступных игроков", value="0"))

        super().__init__(
            placeholder="Выберите игрока",
            options=options,
            custom_id="games3",
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer(with_message=False)

        if not await self._is_current_captain(interaction):
            return await interaction.send("Сейчас выбирает другой капитан.", ephemeral=True)

        if not interaction.values or interaction.values[0] == "0":
            return await interaction.send("❌ Игрок для выбора отсутствует.", ephemeral=True)

        try:
            selected_player_id = int(interaction.values[0])
        except ValueError:
            return await interaction.send("⚠ Некорректный выбор игрока.", ephemeral=True)

        await self._process_selection(interaction, selected_player_id)

    async def _is_current_captain(self, interaction: disnake.MessageInteraction) -> bool:
        fr = await UsersDataBase().get_user(self.ved_id)
        rt = await UsersDataBase().get_user(interaction.user.id)

        if not fr or not rt:
            return False

        return fr[0][15] % 2 + 1 == rt[0][14]

    async def _process_selection(self, interaction: disnake.MessageInteraction, player_id: int):
        guild = self.bot.get_guild(self.guild_serv)
        if guild is None:
            return await interaction.send("⚠ Гильдия не найдена.", ephemeral=True)

        player_data = await UsersDataBase().get_user(player_id)
        if not player_data or player_data[0][12] != 0:
            return await interaction.send("Этот игрок уже в команде.", ephemeral=True)

        fd = await UsersDataBase().get_user(interaction.user.id)
        we = await UsersDataBase().get_user(self.ved_id)

        team_num = fd[0][14]
        await UsersDataBase().update_team(team_num, player_id)
        await UsersDataBase().update_kap1(1, self.ved_id)

        await interaction.send("✅ Вы успешно выбрали игрока", ephemeral=True)

        # Добавляем доступ в голосовые каналы команды
        await self._give_voice_access(guild, team_num, player_id, we)

        # Даём доступ к общему каналу
        await self._give_channel_access(guild, we[0][4], player_id)

        # Проверка на завершение выбора
        await self._check_selection_complete(guild, we, interaction)

    async def _give_voice_access(self, guild, team_num, player_id, we):
        voice_channel_id = we[0][16] if team_num == 1 else we[0][17]
        channel = guild.get_channel(voice_channel_id)
        if channel:
            overwrite = disnake.PermissionOverwrite(view_channel=True, connect=True)
            await channel.set_permissions(guild.get_member(player_id), overwrite=overwrite)

    async def _give_channel_access(self, guild, channel_id, player_id):
        channel = guild.get_channel(channel_id)
        if channel:
            overwrite = disnake.PermissionOverwrite(view_channel=True)
            await channel.set_permissions(guild.get_member(player_id), overwrite=overwrite)

    async def _check_selection_complete(self, guild, we, interaction):
        fr = await UsersDataBase().get_user(self.ved_id)
        if not fr:
            return

        total_picks = int(fr[0][7].split('_')[1][0]) * 2 - 1
        if fr[0][15] != total_picks:
            return

        # Формируем список команд
        popk = await UsersDataBase().get_user_vse(self.ved_id)
        fred = guild.get_channel(we[0][16])
        fred1 = guild.get_channel(we[0][17])

        team1 = f"{fred.name}\n"
        team2 = f"{fred1.name}\n"

        for player in popk:
            if player[1] == player[2] and player[9] == 1:
                if player[12] == 1:
                    team1 += f"<@!{player[2]}> ({player[2]})\n\n"
                elif player[12] == 2:
                    team2 += f"<@!{player[2]}> ({player[2]})\n\n"
            else:
                if player[12] == 1:
                    team1 += f"<@!{player[2]}> ({player[2]})\n\n"
                elif player[12] == 2:
                    team2 += f"<@!{player[2]}> ({player[2]})\n\n"

        embed = disnake.Embed(title="Команды", description=f"{team1}\n\n{team2}")
        polt = guild.get_channel(fr[0][4])
        msg = polt.get_partial_message(fr[0][19])
        await msg.edit(embed=embed, components=None)

        # Закрываем доступ всем
        conf = await UsersDataBase().get_config_by_guild(guild.id)
        role_evri = guild.get_role(conf['role_id_evri'])
        if role_evri:
            overwrite = disnake.PermissionOverwrite(
                view_channel=False,
                mention_everyone=False,
                send_messages=False,
                attach_files=False,
                add_reactions=False,
                manage_messages=False,
                embed_links=False
            )
            await polt.set_permissions(role_evri, overwrite=overwrite)


class SelectGames4(disnake.ui.Select):
    def __init__(self, ved_id: int, guild_serv: int, stop: list[int], rl_name: str, bot: commands.Bot):
        self.ved_id = ved_id
        self.guild_serv = guild_serv
        self.stop = stop
        self.rl_name = rl_name
        self.bot = bot

        guild = self.bot.get_guild(self.guild_serv)
        options = []
        if guild:
            for member_id in self.stop:
                member = guild.get_member(member_id)
                if member:
                    options.append(disnake.SelectOption(label=member.display_name, value=str(member_id)))
        if not options:
            options.append(disnake.SelectOption(label="Нет доступных игроков", value="0"))

        super().__init__(
            placeholder="Выберите игрока",
            options=options,
            custom_id="games4",
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer(with_message=False)

        if not interaction.values or interaction.values[0] == "0":
            return await interaction.send("❌ Игрок для кика отсутствует.", ephemeral=True)

        try:
            val = int(interaction.values[0])
        except ValueError:
            return await interaction.send("⚠ Некорректный выбор игрока.", ephemeral=True)

        # Обновляем базу
        await UsersDataBase().del_user(val)
        await UsersDataBase().update_kol(-1, interaction.user.id)
        await UsersDataBase().add_kik(val, f'{interaction.user.id}')
        await interaction.send("✅ Вы успешно кикнули игрока", ephemeral=True)

        user_id = interaction.user.id
        rl_name = self.rl_name
        guild_id = self.guild_serv

        pur = await UsersDataBase().get_user(user_id)
        if not pur or pur[0][19] != 0:
            return  # Если условие не выполнено — ничего не делать

        if rl_name not in "DOTA2":
            await self._update_general_game(interaction, pur, user_id, guild_id)
        elif rl_name == "DOTA2":
            await self._update_dota2_game(interaction, pur, user_id, guild_id)

    async def _update_general_game(self, interaction, pur, user_id, guild_id):
        rt = await UsersDataBase().get_user_vse(user_id)
        kl = pur[0][7]
        gt = "Капитаны" if pur[0][8] == 2 else "Миксы"

        embed = disnake.Embed(
            title=f"Регистрация на {kl.split('_')[0]} {kl.split('_')[1]} {kl.split('_')[2]}",
            description=f"Зарегистрировалось: {pur[0][10]}/**{int(kl.split('_')[1][0]) * 2}**",
        )

        for i in rt:
            if i[1] == i[2]:
                if i[9] == 1:
                    embed.add_field(name="", value=f"<@!{i[2]}>", inline=False)
            else:
                embed.add_field(name="", value=f"<@!{i[2]}>", inline=False)

        embed.add_field(name="", value=f"<#{pur[0][5]}>\nТип игры: **{gt}**", inline=False)

        channel = self.bot.get_channel(pur[0][4])
        if channel:
            msg = await channel.fetch_message(pur[0][13])
            if msg:
                await msg.edit(embed=embed, components=[
                    disnake.ui.Button(
                        label="Присоединиться",
                        style=disnake.ButtonStyle.blurple,
                        custom_id=f"присоединиться_{user_id}_{guild_id}_{self.rl_name}"
                    )
                ])

    async def _update_dota2_game(self, interaction, pur, user_id, guild_id):
        rt = await UsersDataBase().get_user_vse(user_id)
        kl = pur[0][7]
        gt = "Капитаны" if pur[0][8] == 2 else "Миксы"

        embed = disnake.Embed(
            title=f"Регистрация на {kl.split('_')[0]} {kl.split('_')[1]} {kl.split('_')[2]}",
            description=f"Зарегистрировалось: {pur[0][10]}/**{int(kl.split('_')[1][0]) * 2}**",
        )

        roles = ['1️⃣ Керри', '2️⃣ Мидер', '3️⃣ Хард/Офлейн', '4️⃣ Поддержка', '5️⃣ Полная поддержка']

        for j in range(5):
            role_label = roles[j]
            players_list = f'{role_label}\n'
            for i in rt:
                if i[1] == i[2]:
                    if i[9] == 1 and i[11] == j + 1:
                        players_list += f'<@!{i[2]}>\n'
                else:
                    if i[11] == j + 1:
                        players_list += f'<@!{i[2]}>\n'
            embed.add_field(name="", value=players_list, inline=False)

        embed.add_field(name="", value=f"<#{pur[0][5]}>\nТип игры: **{gt}**", inline=False)

        channel = self.bot.get_channel(pur[0][4])
        if channel:
            msg = await channel.fetch_message(pur[0][13])
            if msg:
                await msg.edit(embed=embed, components=[
                    disnake.ui.Button(label="1️⃣", style=disnake.ButtonStyle.blurple, custom_id=f"дота_1_{user_id}_{guild_id}"),
                    disnake.ui.Button(label="2️⃣", style=disnake.ButtonStyle.blurple, custom_id=f"дота_2_{user_id}_{guild_id}"),
                    disnake.ui.Button(label="3️⃣", style=disnake.ButtonStyle.blurple, custom_id=f"дота_3_{user_id}_{guild_id}"),
                    disnake.ui.Button(label="4️⃣", style=disnake.ButtonStyle.blurple, custom_id=f"дота_4_{user_id}_{guild_id}"),
                    disnake.ui.Button(label="5️⃣", style=disnake.ButtonStyle.blurple, custom_id=f"дота_5_{user_id}_{guild_id}"),
                ])

    async def _update_lol_game(self, interaction, pur, user_id, guild_id):
        rt = await UsersDataBase().get_user_vse(user_id)
        kl = pur[0][7]
        gt = "Капитаны" if pur[0][8] == 2 else "Миксы"

        embed = disnake.Embed(
            title=f"Регистрация на {kl.split('_')[0]} {kl.split('_')[1]} {kl.split('_')[2]}",
            description=f"Зарегистрировалось: {pur[0][10]}/**{int(kl.split('_')[1][0]) * 2}**",
        )

        roles = [
            '<:top:1394363785170518108> Топ',
            '<:jungle:1394363745375097003> Лес',
            '<:middle:1394363757911867423> Мид',
            '<:bot:1394363719085068418> Бот',
            '<:support:1394363773028143225> Саппорт',
        ]

        for j in range(5):
            role_label = roles[j]
            players_list = f'{role_label}\n'
            for i in rt:
                if i[1] == i[2]:
                    if i[9] == 1 and i[11] == j + 1:
                        players_list += f'<@!{i[2]}>\n'
                else:
                    if i[11] == j + 1:
                        players_list += f'<@!{i[2]}>\n'
            embed.add_field(name="", value=players_list, inline=False)

        embed.add_field(name="", value=f"<#{pur[0][5]}>\nТип игры: **{gt}**", inline=False)

        channel = self.bot.get_channel(pur[0][4])
        if channel:
            msg = await channel.fetch_message(pur[0][13])
            if msg:
                await msg.edit(embed=embed, components=[
                    disnake.ui.Button(label="", style=disnake.ButtonStyle.grey, custom_id=f"лол_1_{user_id}_{guild_id}", emoji=roles[0]),
                    disnake.ui.Button(label="", style=disnake.ButtonStyle.grey, custom_id=f"лол_2_{user_id}_{guild_id}", emoji=roles[1]),
                    disnake.ui.Button(label="", style=disnake.ButtonStyle.grey, custom_id=f"лол_3_{user_id}_{guild_id}", emoji=roles[2]),
                    disnake.ui.Button(label="", style=disnake.ButtonStyle.grey, custom_id=f"лол_4_{user_id}_{guild_id}", emoji=roles[3]),
                    disnake.ui.Button(label="", style=disnake.ButtonStyle.grey, custom_id=f"лол_5_{user_id}_{guild_id}", emoji=roles[4]),
                ])

class SelectGames6(disnake.ui.Select):
    def __init__(self, ved_id: int, guild_serv: int, stop: list[int], bot: commands.Bot):
        self.ved_id = ved_id
        self.guild_serv = guild_serv
        self.stop = stop
        self.bot = bot

        guild = self.bot.get_guild(self.guild_serv)
        options = []
        if guild:
            for member_id in self.stop:
                member = guild.get_member(member_id)
                if member:
                    options.append(disnake.SelectOption(label=member.display_name, value=str(member_id)))
        if not options:
            options.append(disnake.SelectOption(label="Нет доступных игроков", value="0"))

        super().__init__(
            placeholder="Выберите игроков",
            options=options,
            custom_id="games6",
            min_values=2,
            max_values=2
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer(with_message=False)

        if not interaction.values or "0" in interaction.values:
            return await interaction.send("❌ Недопустимый выбор игроков.", ephemeral=True)

        try:
            val = int(interaction.values[0])
            val1 = int(interaction.values[1])
        except ValueError:
            return await interaction.send("⚠ Некорректный выбор игроков.", ephemeral=True)

        guild = self.bot.get_guild(self.guild_serv)
        if guild is None:
            return await interaction.send("⚠ Гильдия не найдена.", ephemeral=True)

        fd = await UsersDataBase().get_user(interaction.user.id)
        hop1 = await UsersDataBase().get_user(val)
        hop2 = await UsersDataBase().get_user(val1)

        if not fd or not hop1 or not hop2:
            return await interaction.send("⚠ Ошибка получения данных игроков.", ephemeral=True)

        # Проверяем, что игроки в разных командах
        if hop1[0][12] != hop2[0][12]:
            # Меняем команды местами
            await UsersDataBase().update_team(hop2[0][12], hop1[0][2])
            await UsersDataBase().update_team(hop1[0][12], hop2[0][2])

            await interaction.send("✅ Вы успешно поменяли игроков", ephemeral=True)

            fred = guild.get_channel(fd[0][16])
            fred1 = guild.get_channel(fd[0][17])

            # Устанавливаем права доступа для каждого игрока после обмена
            hop1 = await UsersDataBase().get_user(val)
            hop2 = await UsersDataBase().get_user(val1)
            await self._set_voice_permissions(guild, hop1, val, fred, fred1)
            await self._set_voice_permissions(guild, hop2, val1, fred, fred1)

            try:
                team1, team2 = await self._players(fred, fred1, interaction.user.id)
                # --- обновление эмбеда с составами
                embed = disnake.Embed(title="Команды", description=f"{team1}\n\n{team2}")
                channel = self.bot.get_channel(fd[0][4])
                msg = channel.get_partial_message(fd[0][19])
                await msg.edit(embed=embed, components=None)
            except Exception as e:
                print(f"Ошибка при ограничении доступа: {e}")
        else:
            await interaction.send("❌ Игроки находятся в одной команде", ephemeral=True)

    async def _set_voice_permissions(self, guild, player_data, player_id, channel_team1, channel_team2):
        """
        Устанавливает права доступа к голосовым каналам для игрока в зависимости от команды.
        """
        member = guild.get_member(player_id)
        if member is None:
            return

        team = player_data[0][12]
        ved_id = player_data[0][1]
        user_id = player_data[0][2]

        # Проверка если игрок - капитан (id игрока не совпадает с id веда)
        is_captain = ved_id == user_id

        if team == 1:
            if is_captain:
                # Капитан: доступ к каналу команды 1 и 2 с подключением
                if channel_team2:
                    await channel_team2.set_permissions(member, view_channel=True, connect=True)
                if channel_team1:
                    await channel_team1.set_permissions(member, view_channel=True, connect=True)
            else:
                # Обычный игрок: доступ к своему каналу с подключением, другой канал без подключения
                if channel_team1:
                    await channel_team1.set_permissions(member, view_channel=True, connect=True)
                if channel_team2:
                    await channel_team2.set_permissions(member, view_channel=True, connect=False)

        elif team == 2:
            if is_captain:
                # Капитан: доступ к каналу команды 1 и 2 с подключением
                if channel_team1:
                    await channel_team1.set_permissions(member, view_channel=True, connect=True)
                if channel_team2:
                    await channel_team2.set_permissions(member, view_channel=True, connect=True)
            else:
                # Обычный игрок: доступ к своему каналу с подключением, другой канал без подключения
                if channel_team2:
                    await channel_team2.set_permissions(member, view_channel=True, connect=True)
                if channel_team1:
                    await channel_team1.set_permissions(member, view_channel=True, connect=False)

    async def _players(self, voice_a, voice_b, user_id):
        """Распределяет игроков по командам"""
        team1, team2 = "", ""
        # --- Формируем эмбед команд
        for p in await UsersDataBase().get_user_vse(user_id):

            role_name = self.get_role_name_2(p[11])
            member_str = f"{role_name}\n<@!{p[2]}> ({p[2]})\n\n"

            if p[12] == 1:
                team1 += member_str
            elif p[12] == 2:
                team2 += member_str

        return f"{voice_a.name}\n{team1}", f"{voice_b.name}\n{team2}"
    def get_role_name_2(self, pos):
        roles = {
            1: "1️⃣ Керри",
            2: "2️⃣ Мидер",
            3: "3️⃣ Хард/Офлейн",
            4: "4️⃣ Поддержка",
            5: "5️⃣ Полная поддержка",
        }
        return roles.get(pos, "")

