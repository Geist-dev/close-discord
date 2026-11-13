import disnake
from disnake.ext import commands
from disnake.ui import View, Button

from utils.databases import UsersDataBase

CONFIG_PARTS = (
    ('Основные настройки', (
        ('admin', 'Роль администратора'),
        ('categori_pod_id', 'Категория игровых каналов'),
        ('role_closemod_id', 'Роль ведущего Close'),
        ('role_id_evri', 'Роль @everyone (ID сервера)'),
        ('log', 'Текстовый канал логов'),
    )),
    ('Игры и ограничения', (
        ('closeban_id', 'Роль Closeban'),
        ('log2', 'Второй текстовый канал логов'),
        ('CS2', 'Роль CS2'),
        ('DOTA2', 'Роль Dota 2'),
        ('VALORANT', 'Роль Valorant'),
    )),
    ('Модерация', (
        ('role_otvechclosemod_id', 'Роль старшего модератора'),
        ('channel_close_role_log', 'Канал логов управления ролями'),
    )),
)
ROLE_FIELDS = {'admin', 'role_closemod_id', 'role_id_evri', 'closeban_id', 'CS2', 'DOTA2', 'VALORANT', 'role_otvechclosemod_id'}


def can_configure(inter, guild_id):
    return bool(inter.guild and inter.guild.id == guild_id and inter.user.guild_permissions.manage_guild)


def validate_ids(guild, values):
    result = {}
    for key, raw in values.items():
        raw = raw.strip()
        if not raw.isascii() or not raw.isdigit() or not 0 <= int(raw) < 2**64:
            raise ValueError('Укажите числовые ID. Значение 0 отключает необязательный параметр.')
        value = int(raw)
        if value:
            item = guild.get_role(value) if key in ROLE_FIELDS else guild.get_channel(value)
            if item is None:
                raise ValueError(f'ID {value} не найден на этом сервере.')
            if key == 'categori_pod_id' and not isinstance(item, disnake.CategoryChannel):
                raise ValueError('Для игровых каналов укажите ID категории.')
            if key not in ROLE_FIELDS and key != 'categori_pod_id' and not isinstance(item, disnake.TextChannel):
                raise ValueError('Для логов укажите ID текстового канала.')
        result[key] = value
    return result


class ConfigModal(disnake.ui.Modal):
    def __init__(self, db, guild_id, part, existing_data=None):
        self.db = db
        self.guild_id = guild_id
        self.part = part
        title, fields = CONFIG_PARTS[part]
        existing = existing_data or {}
        super().__init__(title=title, components=[
            disnake.ui.TextInput(
                label=label, custom_id=key, value=str(existing.get(key) or 0),
                placeholder='Числовой ID или 0', max_length=20,
            ) for key, label in fields
        ])

    async def callback(self, inter):
        # Check again when submitting: permissions may have changed since /config.
        if not can_configure(inter, self.guild_id):
            await inter.response.send_message('Нужны права управления этим сервером.', ephemeral=True)
            return
        try:
            data = validate_ids(inter.guild, inter.text_values)
        except ValueError as error:
            await inter.response.send_message(str(error), ephemeral=True)
            return
        await inter.response.defer(ephemeral=True)
        await self.db.save_config_patch(self.guild_id, data)
        await inter.followup.send('Настройки сохранены. Остальные разделы не изменены.', ephemeral=True)


# Keep the existing public class names for extensions/imports.
class ConfigModalPart1(ConfigModal):
    def __init__(self, db, guild_id, existing_data=None):
        super().__init__(db, guild_id, 0, existing_data)


class ConfigModalPart2(ConfigModal):
    def __init__(self, db, guild_id, existing_data=None):
        super().__init__(db, guild_id, 1, existing_data)


class ConfigModalPart3(ConfigModal):
    def __init__(self, db, guild_id, existing_data=None):
        super().__init__(db, guild_id, 2, existing_data)


class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = UsersDataBase()

    @commands.slash_command(description='Настройка каналов, ролей и игр Close Bot')
    @commands.guild_only()
    @commands.default_member_permissions(manage_guild=True)
    async def config(self, inter):
        if not can_configure(inter, inter.guild.id):
            await inter.send('Нужны права управления сервером.', ephemeral=True)
            return
        view = View(timeout=300)
        for part, (title, _) in enumerate(CONFIG_PARTS):
            button = Button(label=f'{part + 1}. {title}', style=disnake.ButtonStyle.secondary)

            async def open_part(button_inter, selected=part):
                if not can_configure(button_inter, inter.guild.id):
                    await button_inter.response.send_message('Нужны права управления сервером.', ephemeral=True)
                    return
                existing = await self.db.get_config_by_guild(inter.guild.id) or {}
                await button_inter.response.send_modal(ConfigModal(self.db, inter.guild.id, selected, existing))

            button.callback = open_part
            view.add_item(button)
        embed = disnake.Embed(
            title='Настройка Close Bot',
            description='Настройте три раздела. Изменения сохраняются отдельно для этого сервера.\n\n'
                        '**1. Основные настройки** — категория, ведущие и журнал.\n'
                        '**2. Игры и ограничения** — игровые роли и Closeban.\n'
                        '**3. Модерация** — старшие модераторы и журнал ролей.\n\n'
                        'Включите режим разработчика Discord и копируйте ID через контекстное меню. '
                        'Значение **0** оставляет параметр отключённым.',
            color=0xB8E89B,
        )
        embed.set_footer(text='Close Bot · Geist-dev')
        await inter.send(embed=embed, view=view, ephemeral=True)


def setup(bot):
    bot.add_cog(ConfigCog(bot))
