import disnake
from disnake.ext import commands
from utils.databases import UsersDataBase



class CloseHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def process_close(self, inter: disnake.AppCmdInter, user_id: int):
        await inter.response.defer(with_message=False)

        # Получаем данные пользователя
        pur = await UsersDataBase().get_user(user_id)

        # Удаляем все записи пользователя
        rrw = await UsersDataBase().get_user_vse(user_id)
        for i in rrw:
            await UsersDataBase().del_user(i[2])

        erty = await UsersDataBase().get_kik_vse(user_id)
        for i in erty:
            await UsersDataBase().del_kik(i[1])

        # Получаем каналы
        fred1 = self.bot.get_channel(pur[0][4])

        fred2 = self.bot.get_channel(pur[0][3])
        fred3 = self.bot.get_channel(pur[0][5])
        category = fred1.category
        # Удаляем каналы
        for ch in [
            fred1, fred2, fred3,
            self.bot.get_channel(pur[0][16]),
            self.bot.get_channel(pur[0][17])
        ]:
            if ch:
                try:
                    await ch.delete()
                except Exception as e:
                    print(f"Не удалось удалить канал {ch}: {e}")

        if category:
            try:
                await category.delete(reason="Удаление категории после удаления каналов")
            except Exception as e:
                print(f"Не удалось удалить категорию {category}: {e}")


def setup(bot):
    bot.add_cog(CloseHandler(bot))
