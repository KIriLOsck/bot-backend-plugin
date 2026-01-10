import aiosqlite
from datetime import datetime
import asyncio

class UserBase:
    def __init__(self, path: str):
        self.path = path

    async def create_table(self):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.cursor()
            await cursor.execute(
                """CREATE TABLE IF NOT EXISTS users (
                    nickname STRING,
                    lastplay INTEGER,
                    lastip STRING,
                    userId STRING
                )"""
            )
            await db.commit()


    async def add_user(self, nickname, userid, lastplay = 0, lastip = "0.0.0.0"):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.cursor()
            await cursor.execute("INSERT OR IGNORE INTO users (nickname, lastplay, lastip, userId) VALUES (?, ?, ?, ?)", (nickname, lastplay, lastip, userid,))
            await db.commit()

    async def update_user(self, nickname, ip):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.cursor()
            await cursor.execute(
                "UPDATE users SET lastplay = ?, lastip = ? WHERE nickname = ?",
                (datetime.now().timestamp(), ip, nickname,)
            )
            await db.commit()


    async def check_user(self, nickname, ip):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.cursor()
            await cursor.execute("SELECT * FROM users WHERE nickname = ?", (nickname,))
            result = await cursor.fetchall()

            if len(result):
                if datetime.now().timestamp() - result[0][1] < 600 and result[0][2] == ip:
                    return True
                else: return False
            return False


    async def get_user(self, nickname):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.cursor()
            await cursor.execute("SELECT * FROM users WHERE nickname = ?", (nickname,))
            result = await cursor.fetchall()

            if len(result):
                return result[0]
            else: return None

    async def get_user_by_id(self, id):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.cursor()
            await cursor.execute("SELECT * FROM users WHERE userId = ?", (id,))
            result = await cursor.fetchall()

            if len(result):
                return result[0]
            else: return None

    async def reset_table(self):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.cursor()
            await cursor.execute("DELETE FROM users")
            await db.commit()



if __name__ == "__main__":
    base = UserBase("base.db")
    asyncio.run(base.create_table())
    # asyncio.run(base.add_user("kirilosck"))
    
