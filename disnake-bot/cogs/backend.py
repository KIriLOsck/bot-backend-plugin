import disnake
import aiohttp
from disnake.ext import commands, tasks
from utils.register import register_user
from config import settings


class BackendIntegration(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.endpoint = settings.SERVER_ENDPOINT
        self.backend_ping.start()
        print(f"Ког {self.__class__.__name__} загружен")


    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_guild(settings.GUILDID).get_channel(settings.EVENT_MESSAGE_CHANNEL)
        async for message in channel.history(limit=10):
            await message.delete()
        views = disnake.ui.View(timeout=None)
        views.add_item(RegestrationButton())

        embed = disnake.Embed(
            title="Регистрация на сервер майнкрафт (+ ивенты)",
            description=
            "Нажмите на кнопку ниже, чтобы зарегистрироваться на сервер майнкрафт. \
            Это необходимо для предотвращения логина под чужим никнеймом. \
            При каждом заходе на сервер в ЛС будет приходить код для входа.\n\n\
            Не забудьте разрешить **ЛС от ботов**, иначе вы не сможете получить код для входа!\n\
            Внимательно проверяйте написание никнейма, для изменения никнейма придёься обратиться к администрации сервера.",
            color=disnake.Color.green()
        )
        await channel.send(embed=embed, view=views)


    @commands.slash_command(name="reset", description="reset table")
    @commands.is_owner()
    async def reset_table(self, inter: disnake.ApplicationCommandInteraction):
        endpoint = self.endpoint + "reset"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint) as request:
                    if request.status == 200:
                        await inter.response.send_message("All is OK")
                    else:
                        await inter.response.send_message(f"Something is wrong: {request.status}")
        except Exception as e:
            await inter.response.send_message(f"Exception: {e}")


    @tasks.loop(seconds=1)
    async def backend_ping(self):
        codes = {}

        async with aiohttp.ClientSession() as session:
            async with session.get(self.endpoint + "codes") as request:
                if request.status == 200:
                    codes = await request.json()
        
        for userid, code in codes.items():
            user = self.bot.get_user(int(userid))
            if user:
                try:
                    await user.send(f"Ваш код для входа: `{code}`")
                except disnake.Forbidden:
                    print(f"Не удалось отправить сообщение пользователю {user.id}")

    def cog_unload(self):
        self.backend_ping.stop()



class RegistrationModal(disnake.ui.Modal):
    def __init__(self):
        super().__init__(
            title="Форма регистрации",
            components=[
                disnake.ui.TextInput(label="Ваш ник в minecraft (регистр не важен)")
            ]
        )


    async def callback(self, inter: disnake.ModalInteraction):
        result = await register_user(inter)
        if result == "nickname_exists":
            await inter.response.send_message("Никнейм уже занят.", ephemeral=True)
        elif result == "userid_exists":
            await inter.response.send_message("Вы уже зарегистрированы.", ephemeral=True)

        else:
            try:
                await inter.author.send(inter.author.mention)
                await inter.author.send("Отлично! Теперь вы будете получать код для входа в личных сообщениях.")
                await inter.response.send_message("Успешно!", ephemeral=True)
            except disnake.Forbidden:
                await inter.response.send_message("У вас закрыты ЛС от ботов. Вы зарегестрированны, но для входа в игру вам нужно будет использовать код, который будет отправлен вам в ЛС.", ephemeral=True)
            except disnake.HTTPException:
                await inter.response.send_message("Не удалось отправить сообщение", ephemeral=True)



class RegestrationButton(disnake.ui.Button):
    def __init__(self):
        super().__init__(
            label="Регистрация",
            style=disnake.ButtonStyle.success,
        )

    async def callback(self, inter: disnake.Interaction):
        await inter.response.send_modal(RegistrationModal())



def setup(bot: commands.Bot):
    bot.add_cog(BackendIntegration(bot))