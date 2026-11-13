"""Local settings; importing this module never connects to Discord."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')


def database_path():
    path = Path(os.getenv('DATABASE_PATH', '.data/users.db'))
    return path if path.is_absolute() else ROOT / path


def test_guild_ids():
    raw = os.getenv('TEST_GUILD_IDS', '').strip()
    try:
        ids = [int(part.strip()) for part in raw.split(',') if part.strip()]
    except ValueError as error:
        raise ValueError('TEST_GUILD_IDS must contain comma-separated numeric server IDs.') from error
    if any(value <= 0 or value >= 2**64 for value in ids):
        raise ValueError('TEST_GUILD_IDS contains an invalid server ID.')
    return ids


def bot_token():
    value = os.getenv('TOKEN', '').strip()
    if not value or value in ('REPLACE_WITH_BOT_TOKEN', 'your_bot_token_here'):
        raise ValueError('Set TOKEN in the local .env file. Never commit or share it.')
    return value
