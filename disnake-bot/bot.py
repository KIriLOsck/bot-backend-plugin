import disnake, os
from disnake.ext import commands
from aiohttp_socks import ProxyConnector
from config import settings
import asyncio

loaded_cogs = []

def load_cog(bot: commands.InteractionBot, cog_name: str):
    try:
        bot.load_extension(f"cogs.{cog_name}")
        print(f"[O] Загружен {cog_name}")
        loaded_cogs.append(cog_name)

    except Exception as e:
        raise disnake.ext.commands.ExtensionFailed(f"Не удалось загрузить ког {cog_name}! Ошибка:\n{e}")


def load_cogs(bot: commands.InteractionBot):
    for path in os.listdir("./cogs"):
        if path.endswith(".py"):
            try:
                load_cog(bot, path[:-3])
            except Exception as e:
                print(f"[X] Не удалось загрузить ког {path[:-3]}\n{e}")
            

def create_bot():
    if settings.USE_PROXY:
        connector = ProxyConnector.from_url(settings.PROXY_URL)
        bot = commands.InteractionBot(
            connector=connector,
            intents=disnake.Intents.all(),
            test_guilds=[settings.TEST_GUILD], 
        )

    else:
        bot = commands.InteractionBot(
            intents=disnake.Intents.all(),
            test_guilds=[settings.TEST_GUILD], 
        )

    load_cogs(bot)
    return bot

async def main():
    bot = create_bot()

    @bot.listen()
    async def on_ready():
        print("[O] Load complecte!")

    @bot.slash_command(name="reload", description="Reload one cog")
    @commands.is_owner()
    async def reload(inter: disnake.ApplicationCommandInteraction, cog: str):
        if cog in loaded_cogs:
            try:
                bot.unload_extension("cogs." + cog)
                load_cog(bot, cog)
                await inter.response.send_message(f"Success! Relaoded {cog}", ephemeral=True)

            except Exception as e:
                await inter.response.send_message(f"Error!\n```{e}```", ephemeral=True)
        else:
            await inter.response.send_message("This cog not load!", ephemeral=True)

    @bot.slash_command(name="cogs", description="Show loaded cogs")
    @commands.is_owner()
    async def show_cogs(inter: disnake.ApplicationCommandInteraction):
        if len(loaded_cogs):
            parse_answer = "```\n```".join(loaded_cogs)
            await inter.response.send_message(f'Loaded cogs:\n```{parse_answer}```')
        else:
            await inter.response.send_message("Noone cogs loaded!")

    await bot.start(settings.BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())