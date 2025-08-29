import disnake
from disnake.ext import commands
from utils.databases import UsersDataBase


class ClearHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def clear_players(self, inter: disnake.MessageInteraction, user_id: int, guild_id: int, rl_name: str):
        """Очистка списка игроков и обновление embed"""
        kasir = await UsersDataBase().get_user(user_id)
        if kasir and kasir[0][16] != 0:
            await inter.send("Можно только во время регистрации", ephemeral=True)
            return

        sd = await UsersDataBase().get_user_vse(user_id)
        k = 0

        for i in sd:
            if i[1] != i[2]:
                await UsersDataBase().del_user(i[2])
            else:
                await UsersDataBase().update_igr(0, user_id)
                k = i[10]

        await UsersDataBase().update_kol(0 - k, user_id)
        await inter.send("Список игроков пуст", ephemeral=True)

        pur = await UsersDataBase().get_user(user_id)
        if not pur:
            return

        kl = pur[0][7]
        game_type = "Капитаны" if pur[0][8] == 2 else "Миксы"

        embed = disnake.Embed(
            title=f"Регистрация на {kl.split('_')[0]} {kl.split('_')[1]} {kl.split('_')[2]}",
            description=f"Зарегистрировалось: {pur[0][10]}/**{int(kl.split('_')[1][0]) * 2}**",
            color=disnake.Color.blurple(),
        )

        rt = await UsersDataBase().get_user_vse(user_id)

        if rl_name != "DOTA2":
            for i in rt:
                if i[1] == i[2] and i[9] == 1:
                    embed.add_field(name="", value=f"<@!{i[2]}>", inline=False)
                elif i[1] != i[2]:
                    embed.add_field(name="", value=f"<@!{i[2]}>", inline=False)

            embed.add_field(name="", value=f"<#{pur[0][5]}>\nТип игры: **{game_type}**", inline=False)

            channel = self.bot.get_channel(pur[0][4])
            msg = channel.get_partial_message(pur[0][13])
            await msg.edit(
                embed=embed,
                components=[
                    disnake.ui.Button(
                        label="Присоединиться",
                        style=disnake.ButtonStyle.blurple,
                        custom_id=f"присоединиться_{user_id}_{guild_id}_{rl_name}"
                    )
                ],
            )

        else:  # DOTA2
            for j in range(5):
                roles = ["1️⃣ Керри", "2️⃣ Мидер", "3️⃣ Хард/Офлейн", "4️⃣ Поддержка", "5️⃣ Полная поддержка"]
                pop = f"{roles[j]}\n"

                for i in rt:
                    if i[1] == i[2] and i[9] == 1 and i[11] == (j + 1):
                        pop += f"<@!{i[2]}>\n"
                    elif i[1] != i[2] and i[11] == (j + 1):
                        pop += f"<@!{i[2]}>\n"

                embed.add_field(name="", value=pop, inline=False)

            embed.add_field(name="", value=f"<#{pur[0][5]}>\nТип игры: **{game_type}**", inline=False)

            channel = self.bot.get_channel(pur[0][4])
            msg = channel.get_partial_message(pur[0][13])
            await msg.edit(
                embed=embed,
                components=[
                    disnake.ui.Button(label="1️⃣", style=disnake.ButtonStyle.blurple, custom_id=f"дота_1_{user_id}_{guild_id}"),
                    disnake.ui.Button(label="2️⃣", style=disnake.ButtonStyle.blurple, custom_id=f"дота_2_{user_id}_{guild_id}"),
                    disnake.ui.Button(label="3️⃣", style=disnake.ButtonStyle.blurple, custom_id=f"дота_3_{user_id}_{guild_id}"),
                    disnake.ui.Button(label="4️⃣", style=disnake.ButtonStyle.blurple, custom_id=f"дота_4_{user_id}_{guild_id}"),
                    disnake.ui.Button(label="5️⃣", style=disnake.ButtonStyle.blurple, custom_id=f"дота_5_{user_id}_{guild_id}")
                ],
            )


def setup(bot: commands.Bot):
    bot.add_cog(ClearHandler(bot))
