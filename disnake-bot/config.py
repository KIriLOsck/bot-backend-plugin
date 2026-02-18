from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    BOT_TOKEN: str
    SERVER_ENDPOINT: str

    GUILDID: int
    TEST_GUILD: int = GUILDID
    EVENT_MESSAGE_CHANNEL: int

    USE_PROXY: bool = False
    PROXY_URL: str = "socks5://localhost:10808"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()