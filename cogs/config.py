import disnake
from disnake.ext import commands
from disnake.ui import View, Button
from utils.databases import UsersDataBase  # твой класс базы


class ConfigModalPart1(disnake.ui.Modal):
    def __init__(self, db: UsersDataBase, guild_id: int, existing_data=None):
        self.db = db
        self.guild_id = guild_id
        existing_data = existing_data or {}

        components = [
            disnake.ui.TextInput(
                label="ID роли администратор",
                custom_id="admin",
                style=disnake.TextInputStyle.short,
                required=True,
                value=str(existing_data.get("admin", ""))
            ),
            disnake.ui.TextInput(
                label="ID категории",
                custom_id="categori_pod_id",
                style=disnake.TextInputStyle.short,
                required=True,
                value=str(existing_data.get("categori_pod_id", ""))
            ),
            disnake.ui.TextInput(
                label="ID роли closemod",
                custom_id="role_closemod_id",
                style=disnake.TextInputStyle.short,
                required=True,
                value=str(existing_data.get("role_closemod_id", ""))
            ),
            disnake.ui.TextInput(
                label="ID роли everyone",
                custom_id="role_id_evri",
                style=disnake.TextInputStyle.short,
                required=True,
                value=str(existing_data.get("role_id_evri", ""))
            ),
            disnake.ui.TextInput(
                label="ID канала логов",
                custom_id="log",
                style=disnake.TextInputStyle.short,
                required=True,
                value=str(existing_data.get("log", ""))
            ),
        ]

        super().__init__(title="Настройка конфига - Часть 1", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        data = {k: v for k, v in inter.text_values.items()}

        # Получаем существующий конфиг (если есть)
        existing = await self.db.get_config_by_guild(self.guild_id) or {}

        # Обновляем данными из части 1
        existing.update(data)

        # Сохраняем в базу
        if existing:
            await self.db.update_config_full(self.guild_id, existing)
            await inter.response.send_message("✅ Конфиг обновлён (часть 1)!", ephemeral=True)
        else:
            await self.db.add_config_full(self.guild_id, existing)
            await inter.response.send_message("✅ Конфиг создан (часть 1)!", ephemeral=True)


class ConfigModalPart2(disnake.ui.Modal):
    def __init__(self, db: UsersDataBase, guild_id: int, existing_data=None):
        self.db = db
        self.guild_id = guild_id
        existing_data = existing_data or {}

        components = [
            disnake.ui.TextInput(
                label="ID роли closeban",
                custom_id="closeban_id",
                style=disnake.TextInputStyle.short,
                required=True,
                value=str(existing_data.get("closeban_id", ""))
            ),
            disnake.ui.TextInput(
                label="ID второго канала с логами",
                custom_id="log2",
                style=disnake.TextInputStyle.short,
                required=True,
                value=str(existing_data.get("log2", ""))
            ),
            disnake.ui.TextInput(
                label="ID роли CS2",
                custom_id="CS2",
                style=disnake.TextInputStyle.short,
                required=True,
                value=str(existing_data.get("CS2", ""))
            ),
            disnake.ui.TextInput(
                label="ID роли DOTA2",
                custom_id="DOTA2",
                style=disnake.TextInputStyle.short,
                required=True,
                value=str(existing_data.get("DOTA2", ""))
            ),
            disnake.ui.TextInput(
                label="ID роли VALORANT",
                custom_id="VALORANT",
                style=disnake.TextInputStyle.short,
                required=True,
                value=str(existing_data.get("VALORANT", ""))
            ),
        ]

        super().__init__(title="Настройка конфига - Часть 2", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        data = {k: v for k, v in inter.text_values.items()}

        existing = await self.db.get_config_by_guild(self.guild_id) or {}

        existing.update(data)

        if existing:
            await self.db.update_config_full(self.guild_id, existing)
            await inter.response.send_message("✅ Конфиг обновлён (часть 2)!", ephemeral=True)
        else:
            await self.db.add_config_full(self.guild_id, existing)
            await inter.response.send_message("✅ Конфиг создан (часть 2)!", ephemeral=True)


class ConfigModalPart3(disnake.ui.Modal):
    def __init__(self, db: UsersDataBase, guild_id: int, existing_data=None):
        self.db = db
        self.guild_id = guild_id
        existing_data = existing_data or {}

        components = [
            disnake.ui.TextInput(
                label="ID роли отвечающих closemod",
                custom_id="role_otvechclosemod_id",
                style=disnake.TextInputStyle.short,
                required=True,
                value=str(existing_data.get("role_otvechclosemod_id", ""))
            ),
            disnake.ui.TextInput(
                label="ID третьего канала логов",
                custom_id="channel_close_role_log",
                style=disnake.TextInputStyle.short,
                required=True,
                value=str(existing_data.get("channel_close_role_log", ""))
            ),
        ]

        super().__init__(title="Настройка конфига - Часть 3", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        data = {k: v for k, v in inter.text_values.items()}

        existing = await self.db.get_config_by_guild(self.guild_id) or {}

        existing.update(data)

        if existing:
            await self.db.update_config_full(self.guild_id, existing)
            await inter.response.send_message("✅ Конфиг обновлён (часть 3)!", ephemeral=True)
        else:
            await self.db.add_config_full(self.guild_id, existing)
            await inter.response.send_message("✅ Конфиг создан (часть 3)!", ephemeral=True)


class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = UsersDataBase()

    @commands.slash_command(description="Настройка конфига")
    async def config(self, inter: disnake.AppCmdInter):
        guild = await UsersDataBase().get_config_by_guild(inter.guild.id)
        if guild == None:
            await self.db.add_config(inter.guild.id, {})
        existing_data = await self.db.get_config_by_guild(inter.guild.id) or {}

        view = View()

        button1 = Button(label="Настройка части 1", style=disnake.ButtonStyle.primary)
        button2 = Button(label="Настройка части 2", style=disnake.ButtonStyle.primary)
        button3 = Button(label="Настройка части 3", style=disnake.ButtonStyle.primary)

        async def part1_callback(button_inter: disnake.MessageInteraction):
            await button_inter.response.send_modal(ConfigModalPart1(self.db, inter.guild.id, existing_data))

        async def part2_callback(button_inter: disnake.MessageInteraction):
            await button_inter.response.send_modal(ConfigModalPart2(self.db, inter.guild.id, existing_data))

        async def part3_callback(button_inter: disnake.MessageInteraction):
            await button_inter.response.send_modal(ConfigModalPart3(self.db, inter.guild.id, existing_data))

        button1.callback = part1_callback
        button2.callback = part2_callback
        button3.callback = part3_callback

        view.add_item(button1)
        view.add_item(button2)
        view.add_item(button3)
        embed = disnake.Embed(
            title="Настройка бота",
            description=f"**Подготовьте заранее все id ниже перечисленные**\n\n・ID роли администратор - роль админимтраторов сервера.\n\n・ID категории - категория под которой будут создаваться close.\n\n・ID роли closemod - роль ребят кто может создавать close.\n\n・ID роли everyone - можно указать просто id сервера.\n\n・ID роли closeban - роль ограничивающая доступ к close.\n\n・ID роли отвечающих closemod - роль ответственных за ребят которые регуют close.\n\n・ID канала логов, ID второго канала с логамиб, ID третьего канала логов - логи проведения close, логи выдачи closeban, логи выдачи остальных ролей (можно указать один канал).\n\n・ID роли CS2, ID роли DOTA2, ID роли VALORANT - роли для упоминания юзеров о том что начался close.",
            color=None,
        )
        if inter.user.avatar == None:  # Аватарка в эмбете для тех у кого нет авы и для тех у кого есть аватарка.
            embed.set_thumbnail(url=inter.user.default_avatar)
        else:
            embed.set_thumbnail(url=inter.user.avatar)
        await inter.send(embed=embed, view=view, ephemeral=True)


def setup(bot):
    bot.add_cog(ConfigCog(bot))
