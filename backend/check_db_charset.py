from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    res = conn.execute(text("SHOW VARIABLES LIKE 'character_set_%';"))
    for row in res:
        print(row)
