"""Create a local token placeholder without overwriting existing settings."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / '.env'
if path.exists():
    print('Using existing .env (unchanged).')
else:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
        output.write('TOKEN=REPLACE_WITH_BOT_TOKEN\nTEST_GUILD_IDS=\nDATABASE_PATH=.data/users.db\n')
    print('Created .env. Set TOKEN locally, then run bash start.sh again.')
