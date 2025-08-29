import disnake
from disnake.ext import commands
from utils.databases import UsersDataBase


class RegistrationHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def start_registration(self, inter: disnake.AppCmdInter, user_id: int, guild_id: int, rl_name: str):
        """
        Запускает регистрацию для пользователя.
        """
        await inter.response.defer(with_message=False)
        pur = await UsersDataBase().get_user(user_id)

        # Проверка, выбрал ли пользователь настройки
        if pur[0][7] == 'нет' or (rl_name != "DOTA2" and pur[0][8] == 0):
            return await inter.send('Вы не выбрали до конца настройки', ephemeral=True)

        kl = pur[0][7]
        print(kl)
        game_type = self._get_game_type(rl_name, pur)
        reg_embed = self._create_registration_embed(kl, pur[0][5], game_type)

        # Кнопки регистрации
        registration_components = self._get_registration_buttons(rl_name, inter.user.id, guild_id)

        # Отправка поста с регистрацией
        reg_channel = self.bot.get_channel(pur[0][4])
        tip = await reg_channel.send(embed=reg_embed, components=registration_components)
        await UsersDataBase().update_messeg2(tip.id, user_id)

        # Кнопки управления матчем
        manage_embed = self._create_manage_embed(inter.user, kl, game_type)
        manage_components = self._get_manage_buttons(inter.user.id, guild_id, rl_name, game_type)

        await inter.edit_original_response(embed=manage_embed, components=manage_components)
        await inter.send('Регистрация началась', ephemeral=True)

    # ================= Вспомогательные методы =================

    def _get_game_type(self, rl_name: str, pur_data) -> str:
        """Возвращает тип игры."""
        if rl_name == "DOTA2":
            return "Миксы"
        return "Капитаны" if pur_data[0][8] == 2 else "Миксы"

    def _create_registration_embed(self, kl: str, text_channel_id: int, game_type: str) -> disnake.Embed:
        """Создаёт embed для поста с регистрацией."""
        return disnake.Embed(
            title=f"Регистрация на {' '.join(kl.split('_')[:3])}",
            description=(
                f"Зарегистрировалось: 0/**{int(kl.split('_')[1][0]) * 2}**\n\n"
                f"<#{text_channel_id}>\n"
                f"Тип игры: **{game_type}**"
            ),
            color=None
        )

    def _create_manage_embed(self, user: disnake.User, kl: str, game_type: str) -> disnake.Embed:
        """Создаёт embed для управления матчем."""
        embed = disnake.Embed(
            title=f"Управление матчем - {user.name}",
            description=f"Формат: **{' '.join(kl.split('_')[:2])}**\nТип матча: **{game_type}**",
            color=None
        )
        embed.set_thumbnail(url=user.avatar or user.default_avatar)
        return embed

    def _get_registration_buttons(self, rl_name: str, user_id: int, guild_id: int):
        """Возвращает список кнопок для регистрации."""
        if rl_name == "DOTA2":
            return [
                disnake.ui.Button(label=f"{i}️⃣", style=disnake.ButtonStyle.blurple,
                                  custom_id=f"дота_{i}_{user_id}_{guild_id}")
                for i in range(1, 6)
            ]
        return [
            disnake.ui.Button(label="Присоединиться", style=disnake.ButtonStyle.blurple,
                              custom_id=f"присоединиться_{user_id}_{guild_id}_{rl_name}")
        ]

    def _get_manage_buttons(self, user_id: int, guild_id: int, rl_name: str, game_type: str):
        """Возвращает список кнопок для управления матчем."""
        return [[
            disnake.ui.Button(label="Начать матч", style=disnake.ButtonStyle.grey,
                              custom_id=f"{game_type}_{user_id}_{guild_id}_{rl_name}",
                              emoji='<:2_:1208208364191092787>'),
            disnake.ui.Button(label="Кикнуть", style=disnake.ButtonStyle.grey,
                              custom_id=f"кикнуть_{user_id}_{guild_id}_{rl_name}",
                              emoji='<:emoji_22:1410623911896551484>'),
            disnake.ui.Button(label="Забанить", style=disnake.ButtonStyle.grey,
                              custom_id=f"Closeban_100_{guild_id}" if rl_name != "DOTA2" else "Closeban_100",
                              emoji='<:image_20250828_191944:1410712955330363585>')],
            [disnake.ui.Button(label="️Удалить матч", style=disnake.ButtonStyle.grey,
                              custom_id=f"удалить_{user_id}_{guild_id}",
                              emoji='<:delete:1410714542291554325>'),
             disnake.ui.Button(label="Управление", style=disnake.ButtonStyle.grey,
                              custom_id=f"миша_{user_id}_{guild_id}_{rl_name}",
                              emoji='<:settings:1410714376733851690>')
        ]]


def setup(bot: commands.Bot):
    bot.add_cog(RegistrationHandler(bot))
