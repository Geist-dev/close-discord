import disnake
from disnake.ext import commands
from utils.databases import UsersDataBase


class CloseRegistrationHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def process_registration(self, inter: disnake.MessageInteraction, user_id: int, guild_id: int, rl_name: str):
        await inter.response.defer(with_message=False)

        user_db = UsersDataBase()

        # Проверка на "кикнутых"
        kicked = await user_db.get_kik(inter.user.id)
        if kicked and inter.user.id == kicked[0][1] and user_id == int(kicked[0][2]):
            await inter.send("Вы не можете записаться на этот Close!", ephemeral=True)
            return

        # Проверка, участвует ли уже в другом Close
        current_game = await user_db.get_user(inter.user.id)
        if current_game and current_game[0][1] != user_id:
            await inter.send("Вы уже участвуете в другом Close!", ephemeral=True)
            return

        # Данные о текущем Close
        host_data = await user_db.get_user(user_id)
        if not host_data:
            await inter.send("Такой Close не найден!", ephemeral=True)
            return

        # Проверка на заполненность
        all_players = await user_db.get_user_vse(user_id)
        max_players = int(host_data[0][7].split('_')[1][0]) * 2
        if (len(all_players) == max_players and host_data[0][9] == 1) or len(all_players) >= max_players + 1:
            await inter.send("Уже максимальное количество игроков записано!", ephemeral=True)
            return

        # Запись или снятие с участия
        if not current_game and inter.user.id != user_id:
            await user_db.add_user(user_id, inter.user.id, 0, 0, 0, 0, inter.guild.id)
            await user_db.update_kol(1, user_id)
        elif inter.user.id == user_id:  # Хост
            new_status = 1 if host_data[0][9] == 0 else 0
            await user_db.update_igr(new_status, user_id)
            await user_db.update_kol(1 if new_status == 1 else -1, user_id)
        else:
            await user_db.del_user(inter.user.id)
            await user_db.update_kol(-1, user_id)

        # Формирование embed
        updated_players = await user_db.get_user_vse(user_id)
        host_data = await user_db.get_user(user_id)
        game_mode = "Капитаны" if host_data[0][8] == 2 else "Миксы"
        kl = host_data[0][7]

        embed = disnake.Embed(
            title=f"Регистрация на {kl.split('_')[0]} {kl.split('_')[1]} {kl.split('_')[2]}",
            description=f"Зарегистрировалось: {host_data[0][10]}/**{max_players}**",
            color=None,
        )

        for player in updated_players:
            if player[2] != user_id:
                embed.add_field(name="", value=f"<@!{player[2]}>", inline=False)
            else:
                if host_data[0][9] == 1:
                    embed.add_field(name="", value=f"<@!{player[2]}>", inline=False)

        embed.add_field(name="", value=f"<#{host_data[0][5]}>\nТип игры: **{game_mode}**", inline=False)

        await inter.edit_original_response(
            embed=embed,
            components=[
                disnake.ui.Button(
                    label="Присоединиться",
                    style=disnake.ButtonStyle.blurple,
                    custom_id=f"присоединиться_{user_id}_{guild_id}_{rl_name}"
                )
            ]
        )
def setup(bot):
    bot.add_cog(CloseRegistrationHandler(bot))