import disnake
from disnake.ext import commands
from utils.databases import UsersDataBase
class Close(commands.Cog):
    @commands.slash_command()
    async def close(self, inter):
        # Here you can paste some code, it will run for every invoked sub-command.
        pass

    @close.sub_command(description='Создание клоузов')
    async def create(self, inter):
        guild = await UsersDataBase().get_config_by_guild(inter.guild.id)
        role = inter.guild.get_role(int(guild['role_closemod_id']))
        if role not in inter.user.roles:
            embed = disnake.Embed(
                title="Создание клоза",
                description=f"<@!{inter.user.id}>, для использования данной команды необходимы следующие роли: <@&{guild['role_closemod_id']}>",
                color=None,
            )
            if inter.user.avatar == None:  # Аватарка в эмбете для тех у кого нет авы и для тех у кого есть аватарка.
                embed.set_thumbnail(url=inter.user.default_avatar)
            else:
                embed.set_thumbnail(url=inter.user.avatar)
            await inter.send(embed=embed, ephemeral=True)
        else:
            er = await UsersDataBase().get_user(inter.user.id)
            if er != []:
                await inter.send('Вы уже участвуйте в Close!', ephemeral=True)
                return
            embed = disnake.Embed(
                title="Создание клоза",
                description=f"<@!{inter.user.id}>, выберите игру в которую хотите поиграть",
                color=None,
            )
            if inter.user.avatar == None:  # Аватарка в эмбете для тех у кого нет авы и для тех у кого есть аватарка.
                embed.set_thumbnail(url=inter.user.default_avatar)
            else:
                embed.set_thumbnail(url=inter.user.avatar)
            await inter.send(embed=embed, components=[  # Вывод и кнопки
                disnake.ui.Button(label="CS2", style=disnake.ButtonStyle.grey,
                                  custom_id=f"CS2_{inter.user.id}_{guild['guild']}"),
                disnake.ui.Button(label="Dota 2", style=disnake.ButtonStyle.grey,
                                  custom_id=f"DOTA2_{inter.user.id}_{guild['guild']}"),
                disnake.ui.Button(label="Valorant", style=disnake.ButtonStyle.grey,
                                  custom_id=f"VALORANT_{inter.user.id}_{guild['guild']}")], ephemeral=True)
def setup(bot):
    bot.add_cog(Close(bot))