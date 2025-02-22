from api.database import get_db

def test_db_connection():
    db = next(get_db())
    assert db is not None
