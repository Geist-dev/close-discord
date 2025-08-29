import aiosqlite
import disnake


class UsersDataBase:
    def __init__(self):
        # Путь к файлу базы данных
        self.name = 'dbs/users.db'

    # =============================
    #       СОЗДАНИЕ ТАБЛИЦ
    # =============================
    async def create_table(self):
        """Создаёт таблицы, если они ещё не существуют"""
        async with aiosqlite.connect(self.name) as db:
            await db.executescript("""
                CREATE TABLE IF NOT EXISTS close (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ved_id INTEGER NOT NULL,
                    nom INTEGER NOT NULL,
                    channel INTEGER NOT NULL,
                    channel1 INTEGER NOT NULL,
                    channel2 INTEGER NOT NULL,
                    messeg INTEGER NOT NULL,
                    format TEXT NOT NULL,
                    tip INTEGER NOT NULL,
                    igr INTEGER NOT NULL,
                    kol INTEGER NOT NULL,
                    rl_name INTEGER NOT NULL,
                    team INTEGER NOT NULL,
                    messeg2 INTEGER NOT NULL,
                    kap INTEGER NOT NULL,
                    kap1 INTEGER NOT NULL,
                    channel3 INTEGER NOT NULL,
                    channel4 INTEGER NOT NULL,
                    event_id INTEGER NOT NULL,
                    messeg3 INTEGER NOT NULL,
                    monet INTEGER NOT NULL,
                    ping INTEGER NOT NULL,
                    id_serv INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS kik (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_user INTEGER NOT NULL,
                    whatkik TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS mut (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild INTEGER NOT NULL,
                    id_user INTEGER NOT NULL,
                    timemut INTEGER NOT NULL,
                    whatmut TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild TEXT NOT NULL,
                    admin TEXT NOT NULL,
                    categori_pod_id TEXT NOT NULL,
                    role_closemod_id TEXT NOT NULL,
                    role_id_evri TEXT NOT NULL,
                    closeban_id TEXT NOT NULL,
                    log INTEGER TEXT NOT NULL,
                    log2 INTEGER TEXT NOT NULL,    
                    CS2 INTEGER TEXT NOT NULL,
                    DOTA2 INTEGER TEXT NOT NULL,
                    VALORANT INTEGER TEXT NOT NULL,
                    role_otvechclosemod_id TEXT NOT NULL,
                    channel_close_role_log TEXT NOT NULL
                );
            """)
            await db.commit()

    # =============================
    #        ЗАПРОСЫ SELECT
    # =============================
    async def get_table(self):
        """Получить все записи из таблицы close"""
        async with aiosqlite.connect(self.name) as db:
            return await (await db.execute("SELECT * FROM close")).fetchall()

    async def get_user(self, nom: int):
        async with aiosqlite.connect(self.name) as db:
            return await (await db.execute("SELECT * FROM close WHERE nom = ?", (nom,))).fetchall()

    async def get_close_on_channel(self, channel: int):
        async with aiosqlite.connect(self.name) as db:
            return await (await db.execute("SELECT * FROM close WHERE channel1 = ?", (channel,))).fetchall()

    async def get_serv(self, serv: int):
        async with aiosqlite.connect(self.name) as db:
            return await (await db.execute("SELECT * FROM close WHERE id_serv = ?", (serv,))).fetchall()

    async def get_user_vse(self, ved_id: int):
        async with aiosqlite.connect(self.name) as db:
            return await (await db.execute("SELECT * FROM close WHERE ved_id = ?", (ved_id,))).fetchall()

    async def get_kik_vse(self, whatkik: int):
        async with aiosqlite.connect(self.name) as db:
            return await (await db.execute("SELECT * FROM kik WHERE whatkik = ?", (str(whatkik),))).fetchall()

    async def get_kik(self, id_user: int):
        async with aiosqlite.connect(self.name) as db:
            return await (await db.execute("SELECT * FROM kik WHERE id_user = ?", (id_user,))).fetchall()

    async def get_mut1(self, timemut: float):
        async with aiosqlite.connect(self.name) as db:
            return await (await db.execute("SELECT * FROM close WHERE monet <= ?", (timemut,))).fetchall()

    async def get_mut2(self, timemut: float):
        async with aiosqlite.connect(self.name) as db:
            return await (await db.execute("SELECT * FROM close WHERE ping <= ?", (timemut,))).fetchall()

    async def get_user_mut(self, id_user: int):
        async with aiosqlite.connect(self.name) as db:
            return await (await db.execute("SELECT * FROM mut WHERE id_user = ?", (id_user,))).fetchall()

    async def get_user_mut_vrem(self, timemut: int):
        async with aiosqlite.connect(self.name) as db:
            return await (await db.execute("SELECT * FROM mut WHERE timemut <= ?", (timemut,))).fetchall()

    # =============================
    #        INSERT / ADD
    # =============================
    async def add_kik(self, id_user: int, whatkik: str):
        async with aiosqlite.connect(self.name) as db:
            await db.execute("INSERT INTO kik (id_user, whatkik) VALUES (?, ?)", (id_user, whatkik))
            await db.commit()

    async def add_user(self, ved_id: int, nom: int, channel: int, channel1: int, channel2: int, messeg: int, id_serv: int):
        async with aiosqlite.connect(self.name) as db:
            await db.execute("""
                INSERT INTO close (
                    ved_id, nom, channel, channel1, channel2, messeg, format, tip, igr, kol, rl_name, team,
                    messeg2, kap, kap1, channel3, channel4, event_id, messeg3, monet, ping, id_serv
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ved_id, nom, channel, channel1, channel2, messeg, 'нет', 0, 0, 0, 0, 0, 0, 0, 1,
                0, 0, 0, 0, 0, 0, id_serv
            ))
            await db.commit()

    async def add_user_mut(self, id_user: int, guild: int, timemut: int, whatmut: str):
        async with aiosqlite.connect(self.name) as db:
            await db.execute("INSERT INTO mut (guild, id_user, timemut, whatmut) VALUES (?, ?, ?, ?)",
                             (guild, id_user, timemut, whatmut))
            await db.commit()

    # =============================
    #        UPDATE
    # =============================
    async def update_delit(self, ved_id: int, nom: int):
        await self._update_field("close", "ved_id", ved_id, nom)

    async def update_format(self, format: str, ved_id: int):
        await self._update_field("close", "format", format, ved_id)

    async def update_tip(self, tip: int, ved_id: int):
        await self._update_field("close", "tip", tip, ved_id)

    async def update_igr(self, igr: int, ved_id: int):
        await self._update_field("close", "igr", igr, ved_id)

    async def update_kol(self, kol: int, ved_id: int):
        await self._update_increment("close", "kol", kol, ved_id)

    async def update_rl_name(self, rl_name: int, nom: int):
        await self._update_field("close", "rl_name", rl_name, nom)

    async def update_team(self, team: int, nom: int):
        await self._update_field("close", "team", team, nom)

    async def update_messeg2(self, messeg2: int, nom: int):
        await self._update_field("close", "messeg2", messeg2, nom)

    async def update_kap(self, kap: int, nom: int):
        await self._update_field("close", "kap", kap, nom)

    async def update_kap1(self, kap1: int, nom: int):
        await self._update_increment("close", "kap1", kap1, nom)

    async def update_channel3(self, channel3: int, nom: int):
        await self._update_field("close", "channel3", channel3, nom)

    async def update_channel4(self, channel4: int, nom: int):
        await self._update_field("close", "channel4", channel4, nom)

    async def update_event_id(self, event_id: int, nom: int):
        await self._update_field("close", "event_id", event_id, nom)

    async def update_messeg3(self, messeg3: int, nom: int):
        await self._update_field("close", "messeg3", messeg3, nom)

    async def update_monet(self, monet: int, nom: int):
        await self._update_field("close", "monet", monet, nom)

    async def update_ping(self, ping: int, nom: int):
        await self._update_field("close", "ping", ping, nom)

    # =============================
    #        DELETE
    # =============================
    async def del_user(self, nom: int):
        await self._delete_row("close", "nom", nom)

    async def del_kik(self, id_user: int):
        await self._delete_row("kik", "id_user", id_user)

    async def del_user_mut(self, id_user: int):
        await self._delete_row("mut", "id_user", id_user)

    # =============================
    #        ВСПОМОГАТЕЛЬНЫЕ
    # =============================
    async def _update_field(self, table: str, column: str, value, nom: int):
        """Обновление одного поля"""
        async with aiosqlite.connect(self.name) as db:
            await db.execute(f"UPDATE {table} SET {column} = ? WHERE nom = ?", (value, nom))
            await db.commit()

    async def _update_increment(self, table: str, column: str, increment: int, nom: int):
        """Инкремент числового значения"""
        async with aiosqlite.connect(self.name) as db:
            await db.execute(f"UPDATE {table} SET {column} = {column} + ? WHERE nom = ?", (increment, nom))
            await db.commit()

    async def _delete_row(self, table: str, column: str, value):
        """Удаление строки по условию"""
        async with aiosqlite.connect(self.name) as db:
            await db.execute(f"DELETE FROM {table} WHERE {column} = ?", (value,))
            await db.commit()
    # =============================
    #        SELECT для config
    # =============================
    async def get_config_all(self):
        """Получить все записи из config"""
        async with aiosqlite.connect(self.name) as db:
            return await (await db.execute("SELECT * FROM config")).fetchall()

    async def get_config_by_guild(self, guild_id: int) -> dict | None:
        """Получить запись config по ID сервера в виде словаря"""
        async with aiosqlite.connect(self.name) as db:
            db.row_factory = aiosqlite.Row  # Позволяет обращаться по ключам
            row = await (await db.execute(
                "SELECT * FROM config WHERE guild = ?",
                (guild_id,)
            )).fetchone()
            return dict(row) if row else None

    # =============================
    #        INSERT для config
    # =============================
    async def add_config(self, guild: int, data: dict):
        # Добавление новой записи в таблицу config, с данными из словаря
        async with aiosqlite.connect(self.name) as db:
            query = """
            INSERT INTO config (
                guild, admin, categori_pod_id, role_closemod_id, role_id_evri,
                closeban_id, log, log2, CS2, DOTA2, VALORANT,
                role_otvechclosemod_id, channel_close_role_log
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (
                guild,
                data.get("admin", 0),
                data.get("categori_pod_id", 0),
                data.get("role_closemod_id", 0),
                data.get("role_id_evri", 0),
                data.get("closeban_id", 0),
                data.get("log", 0),
                data.get("log2", 0),
                data.get("CS2", 0),
                data.get("DOTA2", 0),
                data.get("VALORANT", 0),
                data.get("role_otvechclosemod_id", 0),
                data.get("channel_close_role_log", 0),
            )
            await db.execute(query, values)
            await db.commit()

    async def update_config(self, guild: int, data: dict):
        # Обновление существующей записи
        async with aiosqlite.connect(self.name) as db:
            query = """
            UPDATE config SET
                admin = ?, categori_pod_id = ?, role_closemod_id = ?, role_id_evri = ?,
                closeban_id = ?, log = ?, log2 = ?, CS2 = ?, DOTA2 = ?, VALORANT = ?,
                role_otvechclosemod_id = ?, channel_close_role_log = ?
            WHERE guild = ?
            """
            values = (
                data.get("admin", 0),
                data.get("categori_pod_id", 0),
                data.get("role_closemod_id", 0),
                data.get("role_id_evri", 0),
                data.get("closeban_id", 0),
                data.get("log", 0),
                data.get("log2", 0),
                data.get("CS2", 0),
                data.get("DOTA2", 0),
                data.get("VALORANT", 0),
                data.get("role_otvechclosemod_id", 0),
                data.get("channel_close_role_log", 0),
                guild,
            )
            await db.execute(query, values)
            await db.commit()

    async def update_config_full(
            self,
            guild_id: int,
            data: dict
    ):
        query = """
            UPDATE config SET
                admin = ?,
                categori_pod_id = ?,
                role_closemod_id = ?,
                role_id_evri = ?,
                closeban_id = ?,
                log = ?,
                log2 = ?,
                CS2 = ?,
                DOTA2 = ?,
                VALORANT = ?,
                role_otvechclosemod_id = ?,
                channel_close_role_log = ?
            WHERE guild = ?
        """
        async with aiosqlite.connect(self.name) as db:
            await db.execute(query, (
                int(data.get("admin", 0)),
                int(data.get("categori_pod_id", 0)),
                int(data.get("role_closemod_id", 0)),
                int(data.get("role_id_evri", 0)),
                int(data.get("closeban_id", 0)),
                int(data.get("log", 0)),
                int(data.get("log2", 0)),
                int(data.get("CS2", 0)),
                int(data.get("DOTA2", 0)),
                int(data.get("VALORANT", 0)),
                int(data.get("role_otvechclosemod_id", 0)),
                int(data.get("channel_close_role_log", 0)),
                guild_id
            ))
            await db.commit()