import disnake
from disnake.ext import commands
from utils.databases import UsersDataBase
from cogs.play import PlayCog
from cogs.delete import CloseHandler
from cogs.confirm import RegistrationHandler
from cogs.join import CloseRegistrationHandler
from cogs.join_dota import DotaRegistrationHandler
from cogs.math import MatchHandler
from cogs.mathcap import Matchcap
from cogs.choice import ChoiceCog
from cogs.management import EventManagerCog
from cogs.event import EventCog
from cogs.list import ClearHandler
from cogs.beginning import Closebegin
from cogs.management2 import EventHandler
from cogs.change import Closechange
from cogs.ping import PingHandler
from cogs.closeban import ClosebanCog
from cogs.kik import SelectPlayerCog

from typing import Optional, Tuple


# --- Константы и наборы ключевых слов ---

SKIP_PREFIXES = {"подтвердить", "присоединиться", "Капитаны", "Миксы", "выбор"}

ACTIONS_NEED_CONTEXT = {
    "CS2", "DOTA2", "VALORANT", "удалить", "кикнуть", "забанить",
    "миша", "событие", "список", "снуля", "руслан", "смена", "пинг"
}

RL_REQUIRED_ACTIONS = {
    "кикнуть", "забанить", "миша", "событие", "список",
    "снуля", "руслан", "смена", "завершить", "пинг"
}


def contains_any(text: str, needles: set[str]) -> bool:
    return any(n in text for n in needles)


def _safe_int(s: str) -> Optional[int]:
    try:
        return int(s)
    except Exception:
        return None


# --- Разбор custom_id ---

class CustomId:
    """
    Унифицированный разбор custom_id.
    Старается ничего не менять в исходной схеме и позициях полей.
    """
    def __init__(self, raw: str):
        self.raw = raw
        self.parts = raw.split('_')
        self.action = self.parts[0] if self.parts else raw

    @property
    def is_skip_prefix(self) -> bool:
        return contains_any(self.raw, SKIP_PREFIXES)

    @property
    def is_action_need_context(self) -> bool:
        return contains_any(self.raw, ACTIONS_NEED_CONTEXT)

    @property
    def is_rl_required(self) -> bool:
        # В исходнике это проверялось после нормализации к корню
        return self.action in RL_REQUIRED_ACTIONS or contains_any(self.raw, RL_REQUIRED_ACTIONS)

    def parse_common(self) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        """
        Ожидаемый формат:
        <action>_<user_id>_<guild_id>_<rl_name?>
        """
        user_id = _safe_int(self.parts[1]) if len(self.parts) > 1 else None
        guild_id = _safe_int(self.parts[2]) if len(self.parts) > 2 else None
        rl_name = self.parts[3] if len(self.parts) > 3 else None
        return user_id, guild_id, rl_name

    def parse_podtverdit_vybor(self) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        """
        Для 'подтвердить'/'выбор':
        <action>_<user_id>_<guild_id>_<rl_name>
        """
        return self.parse_common()

    def parse_prisoedinit(self) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        """
        Для 'присоединиться':
        <action>_<user_id>_<guild_id>_<rl_name>
        """
        return self.parse_common()

    def parse_dota(self) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """
        Для 'дота':
        <дота>_<rl_name:int>_<user_id:int>_<guild_id:int>
        """
        rl_name = _safe_int(self.parts[1]) if len(self.parts) > 1 else None
        user_id = _safe_int(self.parts[2]) if len(self.parts) > 2 else None
        guild_id = _safe_int(self.parts[3]) if len(self.parts) > 3 else None
        return rl_name, user_id, guild_id

    def parse_mixy_kapitany(self) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        """
        Для 'Миксы' / 'Капитаны':
        <action>_<user_id>_<guild_id>_<rl_name>
        """
        return self.parse_common()

    def parse_closeban(self) -> Tuple[Optional[int], Optional[int]]:
        """
        Для 'Closeban':
        <Closeban>_<target:int>_<guild_id:int>
        """
        target = _safe_int(self.parts[1]) if len(self.parts) > 1 else None
        guild_id = _safe_int(self.parts[2]) if len(self.parts) > 2 else None
        return target, guild_id

    def normalize_to_action(self, inter: disnake.MessageInteraction):
        """
        inter.component.custom_id = inter.component.custom_id.split('_')[0]
        """
        inter.component.custom_id = self.action


class listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_button_click")
    async def help_listener(self, inter: disnake.MessageInteraction):
        cid = CustomId(inter.component.custom_id)

        # Блок 1: общий фильтр — если нет служебных префиксов
        if not cid.is_skip_prefix:
            if cid.is_action_need_context:
                # Ожидаемый общий формат для большинства действий
                user_id, guild_id, rl_name = cid.parse_common()

                # Проверка RL-доступа (frik[0][13] != 0) — для ряда действий
                if cid.is_rl_required:
                    frik = await UsersDataBase().get_user(user_id)
                    if frik and frik[0][13] == 0:
                        await inter.send('Управление не доступно', ephemeral=True)
                        return

                # Нормализуем custom_id к корню
                cid.normalize_to_action(inter)

                # Только ведущий для RL_REQUIRED_ACTIONS
                if inter.component.custom_id in RL_REQUIRED_ACTIONS and user_id != inter.user.id:
                    await inter.send('Вы не являетесь ведущим', ephemeral=True)
                    return

                # Спец: "удалить" — допускается роль из конфига
                if inter.component.custom_id == "удалить":
                    guild = self.bot.get_guild(guild_id) if guild_id else None
                    if guild:
                        conf2 = await UsersDataBase().get_config_by_guild(guild_id)
                        role_closemod_id = int(conf2['role_otvechclosemod_id'])
                        role_closemod = guild.get_role(role_closemod_id)
                        if user_id != inter.user.id and (role_closemod not in inter.user.roles):
                            await inter.send('Вы не являетесь ведущим', ephemeral=True)
                            return

                # Ещё раз нормализуем (как в исходнике)
                inter.component.custom_id = inter.component.custom_id.split('_')[0]

        # Блок 2: "подтвердить" / "выбор"
        if ("подтвердить" in cid.raw) or ("выбор" in cid.raw):
            user_id, guild_id, rl_name = cid.parse_podtverdit_vybor()
            cid.normalize_to_action(inter)

            # Все кроме "выбор" — только ведущий
            if user_id != inter.user.id and inter.component.custom_id != "выбор":
                await inter.send('Вы не являетесь ведущим', ephemeral=True)
                return

        # Блок 3: "присоединиться"
        if "присоединиться" in cid.raw:
            user_id, guild_id, rl_name = cid.parse_prisoedinit()
            cid.normalize_to_action(inter)

        # Блок 4: "дота" — особый порядок
        if "дота" in cid.raw:
            rl_name, user_id, guild_id = cid.parse_dota()
            cid.normalize_to_action(inter)

        # Блок 5: "Миксы" / "Капитаны" — только ведущий
        if ("Миксы" in cid.raw) or ("Капитаны" in cid.raw):
            user_id, guild_id, rl_name = cid.parse_mixy_kapitany()
            cid.normalize_to_action(inter)
            if user_id != inter.user.id:
                await inter.send('Вы не являетесь ведущим', ephemeral=True)
                return

        # Блок 6: "Closeban"
        if "Closeban" in cid.raw:
            target, guild_id = cid.parse_closeban()
            cid.normalize_to_action(inter)
        if inter.component.custom_id not in ["CS2", "DOTA2", "VALORANT",
                                             "подтвердить", "присоединиться", "дота", "Капитаны", "Миксы",
                                             "выбор", "удалить", "кикнуть", "миша", "событие", "список",
                                             "снуля", "руслан", "смена", "пинг", "Closeban"]:
            return
        if inter.component.custom_id == "CS2" or inter.component.custom_id == "DOTA2" or inter.component.custom_id == "VALORANT":
            play_cog = PlayCog(self.bot)
            await play_cog.create_close(inter, inter.component.custom_id)
        elif inter.component.custom_id == "удалить":
            close_handler = CloseHandler(self.bot)
            await close_handler.process_close(inter, user_id)
        elif inter.component.custom_id == "подтвердить":
            reg_handler = RegistrationHandler(self.bot)
            await reg_handler.start_registration(inter, user_id, guild_id, rl_name)
        elif inter.component.custom_id == "присоединиться":
            close_handler = CloseRegistrationHandler(self.bot)
            await close_handler.process_registration(inter, int(user_id), int(guild_id), rl_name)
        elif inter.component.custom_id == "дота":
            close_handler_dota = DotaRegistrationHandler(self.bot)
            await close_handler_dota.process_dota_registration(inter, int(user_id), int(guild_id), rl_name)
        elif inter.component.custom_id == "Миксы":
            match_handler = MatchHandler(self.bot)
            await match_handler.open_modal(inter, int(user_id), int(guild_id), rl_name)
        elif inter.component.custom_id == "Капитаны":
            match_cap = Matchcap(self.bot)
            await match_cap.create_close(inter, rl_name)
        elif inter.component.custom_id == "выбор":
            choice_cap = ChoiceCog(self.bot)
            await choice_cap.choice_close(inter, user_id)
        elif inter.component.custom_id == "миша":
            event_manager = EventManagerCog(self.bot)
            await event_manager.open_event_manager(inter, int(user_id), int(guild_id), rl_name)
        elif inter.component.custom_id == "событие":
            event_cog = EventCog(self.bot)
            await event_cog.toggle_event(inter, int(user_id), int(guild_id), rl_name)
        elif inter.component.custom_id == "список":
            clear_handler = ClearHandler(self.bot)
            await clear_handler.clear_players(inter, int(user_id), int(guild_id), rl_name)
        elif inter.component.custom_id == "снуля":
            close_beginning = Closebegin(self.bot)
            await close_beginning.process_close(inter, user_id, guild_id, rl_name)
        elif inter.component.custom_id == "руслан":
            event_handler = EventHandler(self.bot)
            await event_handler.manage_event(inter, int(user_id), int(guild_id), rl_name)
        elif inter.component.custom_id == "смена":
            change_cog = Closechange(self.bot)
            await change_cog.create_close(inter, rl_name)
        elif inter.component.custom_id == "пинг":
            ping_handler = PingHandler(self.bot)
            await ping_handler.process_ping(inter, int(user_id), int(guild_id), rl_name)
        elif inter.component.custom_id == "Closeban":
            closeban = ClosebanCog(self.bot)
            await closeban.open_closeban_modal(inter)
        elif inter.component.custom_id == "кикнуть":
            select_cog = SelectPlayerCog(self.bot)
            await select_cog.open_player_selector(inter, user_id, guild_id, rl_name)


def setup(bot):
    bot.add_cog(listener(bot))