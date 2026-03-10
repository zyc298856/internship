from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    res = conn.execute(text("SELECT id, content FROM messages ORDER BY id DESC LIMIT 5"))
    for row in res:
        print(row.id, repr(row.content))
