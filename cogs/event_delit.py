from __future__ import annotations

import asyncio
import disnake
from disnake.ext import commands

from utils.databases import UsersDataBase


class CloseAutoCleanupOnChannelDelete(commands.Cog):

    IDX = {
        "id": 0,
        "ved_id": 1,
        "nom": 2,
        "channel": 3,
        "channel1": 4,
        "channel2": 5,
        "channel3": 16,
        "channel4": 17,
        "id_serv": 22,
    }
    CHANNEL_COLS = ("channel", "channel1", "channel2", "channel3", "channel4")

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = UsersDataBase()

    async def _deleted_by_bot(self, guild: disnake.Guild, channel_id: int) -> bool:
        """Проверяем по аудит-логу, что удаление канала сделал сам бот."""
        try:
            if not guild.me.guild_permissions.view_audit_log:
                return False

            # Небольшая задержка: иногда запись в аудит-лог попадает не мгновенно
            for _ in range(3):
                async for entry in guild.audit_logs(
                    limit=6,
                    action=disnake.AuditLogAction.channel_delete
                ):
                    # entry.target — удалённый канал
                    tgt_id = getattr(entry.target, "id", None)
                    usr_id = getattr(entry.user, "id", None)
                    if tgt_id == channel_id and usr_id == self.bot.user.id:
                        return True
                await asyncio.sleep(0.6)
        except Exception as e:
            print(f"[CloseAutoCleanup] Ошибка чтения аудит-лога: {e}")
        return False

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: disnake.abc.GuildChannel):
        guild = channel.guild
        deleted_id = int(channel.id)

        try:
            # Если канал удалил сам бот — ничего не делаем
            if await self._deleted_by_bot(guild, deleted_id):
                print(f"[CloseAutoCleanup] Пропуск: канал {deleted_id} удалён самим ботом.")
                return

            rows = await self.db.get_serv(guild.id)
            if not rows:
                return

            affected_ved_ids: set[int] = set()
            for row in rows:
                for col in self.CHANNEL_COLS:
                    col_val = row[self.IDX[col]]
                    try:
                        if int(col_val) == deleted_id:
                            affected_ved_ids.add(int(row[self.IDX["ved_id"]]))
                            break
                    except (TypeError, ValueError):
                        continue

            if not affected_ved_ids:
                return

            for ved_id in affected_ved_ids:
                close_rows = await self.db.get_user_vse(ved_id)
                if not close_rows:
                    continue

                channels_to_delete: set[int] = set()
                for r in close_rows:
                    for col in self.CHANNEL_COLS:
                        val = r[self.IDX[col]]
                        try:
                            cid = int(val)
                            if cid and cid != deleted_id:
                                channels_to_delete.add(cid)
                        except (TypeError, ValueError):
                            continue

                for cid in list(channels_to_delete):
                    ch = self.bot.get_channel(cid)
                    if ch:
                        try:
                            await ch.delete(reason=f"Close auto-cleanup (ved_id={ved_id}) after channel delete {deleted_id}")
                        except Exception as e:
                            print(f"[CloseAutoCleanup] Не удалось удалить канал {cid}: {e}")

                kik_rows = await self.db.get_kik_vse(ved_id)
                for kr in kik_rows:
                    try:
                        await self.db.del_kik(kr[1])  # id_user
                    except Exception as e:
                        print(f"[CloseAutoCleanup] Не удалось del_kik id_user={kr[1]}: {e}")

                for r in close_rows:
                    nom = int(r[self.IDX["nom"]])
                    try:
                        await self.db.del_user(nom)
                    except Exception as e:
                        print(f"[CloseAutoCleanup] Не удалось del_user nom={nom}: {e}")

        except Exception as e:
            print(f"[CloseAutoCleanup] Ошибка обработки удаления канала {deleted_id}: {e}")


def setup(bot: commands.Bot):
    bot.add_cog(CloseAutoCleanupOnChannelDelete(bot))
