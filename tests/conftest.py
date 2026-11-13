import pytest
from utils.databases import UsersDataBase


@pytest.fixture
async def database(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH', str(tmp_path / 'test.db'))
    db = UsersDataBase()
    await db.create_table()
    return db
