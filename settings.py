from environs import Env
from dataclasses import dataclass


@dataclass
class Bots:
    TELEGRAM_TOKEN: str
    TELEGRAM_ADMIN_CHAT_ID: int
    OPENWEATHERMAP_TOKEN: str


@dataclass
class Settings:
    bots: Bots


def get_settings(path: str):
    env = Env()
    env.read_env(path)

    return Settings(
        bots=Bots(
            TELEGRAM_TOKEN=env.str('TELEGRAM_TOKEN'),
            TELEGRAM_ADMIN_CHAT_ID=env.int('TELEGRAM_ADMIN_CHAT_ID'),
            OPENWEATHERMAP_TOKEN=env.str('OPENWEATHERMAP_TOKEN')
        )
    )


settings = get_settings('secret_key')
