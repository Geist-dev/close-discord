import disnake
from disnake.ext import commands
from utils.databases import UsersDataBase


class DotaRegistrationHandler(commands.Cog):
    ROLE_NAMES = {
        1: "1️⃣ Керри",
        2: "2️⃣ Мидер",
        3: "3️⃣ Хард/Офлейн",
        4: "4️⃣ Поддержка",
        5: "5️⃣ Полная поддержка"
    }

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def process_dota_registration(
        self,
        inter: disnake.MessageInteraction,
        user_id: int,
        guild_id: int,
        rl_name: int
    ):
        await inter.response.defer(with_message=False)
        db = UsersDataBase()

        # --- Данные игрока и хоста ---
        kicked = await db.get_kik(inter.user.id)
        host_data = await db.get_user(user_id)
        all_players = await db.get_user_vse(user_id)
        current_game = await db.get_user(inter.user.id)

        # --- 1. Проверка на кик ---
        if kicked and inter.user.id == kicked[0][1] and user_id == int(kicked[0][2]):
            return await inter.send("Вы не можете записаться на этот Close!", ephemeral=True)

        # --- 2. Проверка, что Close существует ---
        if not host_data:
            return await inter.send("Такой Close не найден!", ephemeral=True)

        # --- 3. Лимит игроков ---
        match_format = host_data[0][7]  # например "Dota_2x2_RU"
        team_size = int(match_format.split('_')[1][0])
        max_players = team_size * 2
        if (len(all_players) == max_players and host_data[0][9] == 1) or len(all_players) >= max_players + 1:
            return await inter.send("Уже максимальное количество игроков записано!", ephemeral=True)

        # --- 4. Игрок уже в другом Close ---
        if current_game and current_game[0][1] != user_id:
            return await inter.send("Вы уже участвуете в другом Close!", ephemeral=True)

        # --- 5. Определение допустимых ролей по формату ---
        taken_roles = [p[11] for p in all_players if p[11] != 0]  # роли всех, кроме ведущего
        allowed_roles = set()

        if taken_roles:
            # Если уже кто-то записался — список допустимых ролей фиксируем
            allowed_roles = set(taken_roles)
        else:
            # Если первый игрок — можно выбирать любые
            allowed_roles = set(self.ROLE_NAMES.keys())

        # Допускаем только нужное кол-во разных ролей в зависимости от team_size
        if len(allowed_roles) > team_size:
            allowed_roles = set(list(allowed_roles)[:team_size])
        # Если выбранная роль не разрешена — отказываем
        if rl_name not in allowed_roles and allowed_roles != {} and len(allowed_roles) >= team_size:
            return await inter.send(
                f"Вы можете выбрать только одну из разрешённых ролей: {', '.join(self.ROLE_NAMES[r] for r in allowed_roles)}",
                ephemeral=True
            )

        # --- 6. Ограничение по роли ---
        same_role_count = sum(1 for p in all_players if p[11] == rl_name)
        if same_role_count >= 2:
            return await inter.send("Уже записаны 2 человека на эту роль", ephemeral=True)

        # --- 7. Запись/снятие ---
        if not current_game and inter.user.id != user_id:
            await db.add_user(user_id, inter.user.id, 0, 0, 0, 0, inter.guild.id)
            await db.update_kol(1, user_id)
            await db.update_rl_name(rl_name, inter.user.id)

        elif inter.user.id == user_id:
            new_status = 1 if host_data[0][9] == 0 else 0
            await db.update_igr(new_status, user_id)
            await db.update_kol(1 if new_status else -1, user_id)
            await db.update_rl_name(rl_name if new_status else 0, user_id)

        else:
            await db.del_user(inter.user.id)
            await db.update_kol(-1, user_id)
            await db.update_rl_name(0, inter.user.id)

        # --- 8. Перечитать данные ---
        updated_players = await db.get_user_vse(user_id)
        host_data = await db.get_user(user_id)
        game_mode = "Капитаны" if host_data[0][8] == 2 else "Миксы"

        # --- 9. Формируем эмбед ---
        embed = disnake.Embed(
            title=f"Регистрация на {match_format.split('_')[0]} {match_format.split('_')[1]} {match_format.split('_')[2]}",
            description=f"Зарегистрировалось: {host_data[0][10]}/**{max_players}**",
            color=None
        )

        for role_id, role_name in self.ROLE_NAMES.items():
            role_block = [role_name]
            for player in updated_players:
                if player[11] != role_id:
                    continue
                is_host = player[1] == player[2]
                if is_host and player[9] != 1:
                    continue
                role_block.append(f"<@!{player[2]}>")
            embed.add_field(name="", value="\n".join(role_block), inline=False)

        embed.add_field(
            name="",
            value=f"<#{host_data[0][5]}>\nТип игры: **{game_mode}**",
            inline=False
        )

        # --- 10. Кнопки ---
        buttons = [
            disnake.ui.Button(
                label=f"{role_id}️⃣",
                style=disnake.ButtonStyle.blurple,
                custom_id=f"дота_{role_id}_{user_id}_{guild_id}"
            )
            for role_id in self.ROLE_NAMES
        ]

        await inter.edit_original_response(embed=embed, components=buttons)


def setup(bot):
    bot.add_cog(DotaRegistrationHandler(bot))
