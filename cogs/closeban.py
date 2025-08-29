# cogs/closeban.py
import time
import disnake
from disnake.ext import commands
from disnake.ui import TextInput, Modal
from disnake import TextInputStyle
from utils.databases import UsersDataBase



class ClosebanModal(Modal):
    """Модалка для выдачи Closeban"""

    def __init__(self, target: int | None, guild_id: int, bot: commands.Bot):
        self.target = target  # может быть id или 100 (ручной ввод)
        self.guild_id = guild_id
        self.bot = bot

        # Базовые поля
        components = [
            TextInput(
                label="Причина бана",
                placeholder="например: нарушение правил",
                custom_id="reason",
                style=TextInputStyle.paragraph,
            ),
            TextInput(
                label="Длительность бана",
                placeholder="например: 1d или 1h",
                custom_id="duration",
                style=TextInputStyle.short,
                max_length=50,
            ),
        ]

        # Если нужно указать id вручную
        if self.target == 100:
            components.insert(
                0,
                TextInput(
                    label="ID участника",
                    placeholder="например: 100398248257278462819",
                    custom_id="member_id",
                    style=TextInputStyle.short,
                    max_length=50,
                ),
            )

        super().__init__(title="Укажите данные для Closeban", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer(with_message=False)

        guild = self.bot.get_guild(self.guild_id)

        # Если target == 100 → админ вводит ID вручную
        if self.target == 100:
            member_id = inter.text_values["member_id"]
            if not member_id.isdigit():
                await inter.send("❌ В ID должны быть только цифры", ephemeral=True)
                return

            member = guild.get_member(int(member_id))
            if not member:
                await inter.send("❌ Нет пользователя с таким ID на сервере", ephemeral=True)
                return

            self.target = member.id

        duration_text = inter.text_values["duration"]

        # Проверяем формат длительности
        if not (duration_text[:-1].isdigit() and duration_text[-1] in ["h", "d"]):
            await inter.send(
                embed=disnake.Embed(
                    title="Ошибка ввода данных",
                    description=(
                        "Введите корректное сообщение.\n\nПримеры:\n"
                        "・ **5d** — 5 дней\n"
                        "・ **1h** — 1 час\n"
                        "・ причина бана: 1.1 или 1.3"
                    ),
                ),
                ephemeral=True,
            )
            return

        # Проверка в базе (уже есть бан?)
        existing_ban = await UsersDataBase().get_user_mut(self.target)
        if existing_ban:
            await inter.send("❌ Пользователь уже имеет Closeban!", ephemeral=True)
            return

        # Преобразуем длительность
        multiplier = 60 if duration_text[-1] == "h" else 1440
        unit = "ч." if duration_text[-1] == "h" else "д."
        duration_seconds = int(duration_text[:-1]) * multiplier * 60
        end_time = time.time() + duration_seconds

        # Логи
        embed = disnake.Embed(title="Логи — Closeban")
        embed.add_field(name="> Тип", value="```closeban```", inline=True)
        for key, value in inter.text_values.items():
            embed.add_field(name=f"> {key}", value=f"```\n{value[:1024]}```", inline=True)

        embed.add_field(
            name="> Исполнитель",
            value=f"・ <@!{inter.user.id}>\n・ {inter.user.id}",
            inline=True,
        )
        embed.add_field(
            name="> Нарушитель",
            value=f"・ <@!{self.target}>\n・ {self.target}",
            inline=True,
        )
        conf = await UsersDataBase().get_config_by_guild(inter.guild.id)
        log_channel = self.bot.get_channel(int(conf["log"]))
        if log_channel:
            await log_channel.send(embed=embed)

        # Выдаём роль Closeban
        role = guild.get_role(int(conf["closeban_id"]))
        member = guild.get_member(self.target)

        if role and member and role not in member.roles:
            await member.add_roles(role)
            await inter.send("✅ Вы выдали Closeban!", ephemeral=True)

        # Записываем в базу
        await UsersDataBase().add_user_mut(
            member.id, guild.id, end_time, inter.text_values["reason"]
        )


class ClosebanCog(commands.Cog):
    """Ког для работы с Closeban"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def open_closeban_modal(self, inter):
        """Открыть модалку Closeban"""
        target = 100
        modal = ClosebanModal(target, inter.guild.id, self.bot)
        await inter.response.send_modal(modal)


def setup(bot: commands.Bot):
    bot.add_cog(ClosebanCog(bot))
