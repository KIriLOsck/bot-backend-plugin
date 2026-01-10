import disnake
import aiohttp
import os

async def register_user(inter: disnake.ModalInteraction):
    endpoint = os.getenv("SERVER_ENDPOINT")
    endpoint += "register"

    data = {
        "nickname": str(inter.data["components"][0]['components'][0]["value"]),
        "userid": str(inter.author.id)
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, json=data) as request:
            if request.status == 200:
                return
            
            elif request.status == 400:
                answer = await request.json()
                detail = answer.get("detail", "")

                if detail == "Nickname already exists":
                    return "nickname_exists"
                elif detail == "UserID already exists":
                    return "userid_exists"
                else:
                    await inter.author.send(detail)
            else:
                await inter.author.send(f"Произошла ошибка при регистрации: {request.status}")