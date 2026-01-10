import disnake
from disnake.ext import commands

class ToolCommands(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="ping", description="Bot ping")
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        latency = self.bot.latency * 1000

        embed = disnake.Embed(
            title="Pong!",
            description=f"Latency: `{round(latency)}`",
            color=0x55FF00
        )

        await inter.response.send_message(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(ToolCommands(bot))