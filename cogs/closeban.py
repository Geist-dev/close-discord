"""Closeban controls with per-guild authorization and recoverable expiry."""
import logging
import re
from time import time

import disnake
from disnake.ext import commands

from utils.databases import UsersDataBase

log = logging.getLogger('closebot.moderation')


async def can_manage_bans(inter):
    if not inter.guild:
        return False
    if inter.user.guild_permissions.manage_guild:
        return True
    config = await UsersDataBase().get_config_by_guild(inter.guild.id)
    if not config:
        return False
    privileged = {int(config.get(key) or 0) for key in ('admin', 'role_otvechclosemod_id')}
    if any(role.id in privileged for role in inter.user.roles):
        return True
    rows = await UsersDataBase().get_user(inter.user.id)
    return bool(rows and int(rows[0][1]) == inter.user.id and int(rows[0][22]) == inter.guild.id and rows[0][13])


def duration_seconds(raw):
    match = re.fullmatch(r'([1-9][0-9]{0,3})([hd])', raw.strip().lower())
    if not match:
        raise ValueError('Укажите срок, например 1h или 5d, от 1 часа до 365 дней.')
    seconds = int(match[1]) * (3600 if match[2] == 'h' else 86400)
    if seconds > 365 * 86400:
        raise ValueError('Максимальный срок Closeban — 365 дней.')
    return seconds


class ClosebanModal(disnake.ui.Modal):
    def __init__(self, target, guild_id, bot):
        self.target, self.guild_id, self.bot = target, guild_id, bot
        fields = [
            disnake.ui.TextInput(label='Причина ограничения', custom_id='reason', style=disnake.TextInputStyle.paragraph, max_length=900),
            disnake.ui.TextInput(label='Длительность: 1h или 5d', custom_id='duration', max_length=6),
        ]
        if target == 100:
            fields.insert(0, disnake.ui.TextInput(label='ID участника', custom_id='member_id', max_length=20))
        super().__init__(title='Closeban', components=fields)

    async def callback(self, inter):
        if not inter.guild or inter.guild.id != self.guild_id or not await can_manage_bans(inter):
            await inter.response.send_message('Недостаточно прав для Closeban на этом сервере.', ephemeral=True)
            return
        try:
            seconds = duration_seconds(inter.text_values['duration'])
            target_id = int(inter.text_values['member_id']) if self.target == 100 else int(self.target)
        except (ValueError, KeyError, TypeError) as error:
            await inter.response.send_message(str(error) if isinstance(error, ValueError) else 'Проверьте ID и срок ограничения.', ephemeral=True)
            return
        await inter.response.defer(ephemeral=True)
        db = UsersDataBase()
        config = await db.get_config_by_guild(self.guild_id)
        role = inter.guild.get_role(int((config or {}).get('closeban_id') or 0))
        member = inter.guild.get_member(target_id)
        if role is None or member is None:
            await inter.followup.send('Участник или роль Closeban не найдены. Проверьте /config.', ephemeral=True)
            return
        if member.bot or member.id == inter.guild.owner_id:
            await inter.followup.send('Нельзя ограничить бота или владельца сервера.', ephemeral=True)
            return
        if await db.get_user_mut(target_id, self.guild_id):
            await inter.followup.send('У участника уже есть активный Closeban.', ephemeral=True)
            return
        try:
            await member.add_roles(role, reason=f'Closeban: {inter.text_values["reason"][:400]}')
        except disnake.HTTPException:
            await inter.followup.send('Не удалось выдать роль. Проверьте права и положение роли бота.', ephemeral=True)
            return
        try:
            await db.add_user_mut(target_id, self.guild_id, int(time()) + seconds, inter.text_values['reason'])
        except Exception:
            # Do not leave a new restriction without an expiry record.
            try:
                await member.remove_roles(role, reason='Не удалось сохранить срок Closeban')
            except disnake.HTTPException:
                log.error('Manual role removal required: guild=%s user=%s', self.guild_id, target_id)
            await inter.followup.send('Не удалось сохранить срок ограничения. Проверьте журнал бота.', ephemeral=True)
            return
        await inter.followup.send('Closeban выдан. По истечении срока роль будет снята автоматически.', ephemeral=True)
        channel = inter.guild.get_channel(int(config.get('log') or 0))
        if channel:
            embed = disnake.Embed(title='Closeban выдан', description=inter.text_values['reason'], color=0xE6B675)
            embed.add_field(name='Участник', value=f'<@{target_id}>')
            embed.add_field(name='Срок', value=inter.text_values['duration'])
            embed.set_footer(text='Close Bot · Geist-dev')
            try:
                await channel.send(embed=embed, allowed_mentions=disnake.AllowedMentions.none())
            except disnake.HTTPException:
                log.warning('Could not send moderation log for guild=%s', self.guild_id)


class ClosebanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def open_closeban_modal(self, inter):
        if not await can_manage_bans(inter):
            await inter.response.send_message('Недостаточно прав для Closeban.', ephemeral=True)
            return
        await inter.response.send_modal(ClosebanModal(100, inter.guild.id, self.bot))


def setup(bot):
    bot.add_cog(ClosebanCog(bot))
