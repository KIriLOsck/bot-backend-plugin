from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    BOT_TOKEN: str
    SERVER_ENDPOINT: str

    GUILDID: int = 1246829700630839431
    TEST_GUILD: int = 1246829700630839431
    EVENT_MESSAGE_CHANNEL: int = 1246829703818514534

    USE_PROXY: bool = False
    PROXY_URL: str = "socks5://localhost:10808"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()