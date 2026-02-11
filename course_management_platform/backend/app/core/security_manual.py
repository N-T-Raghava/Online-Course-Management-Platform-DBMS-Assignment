from passlib.context import CryptContext
import psycopg2

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

conn = psycopg2.connect(
    "postgresql://23CS30035:fu@10.5.18.103:5432/23CS30035"
)

cur = conn.cursor()

# Fetch users
cur.execute("SELECT user_id, password FROM users;")
users = cur.fetchall()

for user_id, plain_pw in users:

    # Skip already hashed
    if plain_pw.startswith("$2b$"):
        continue

    hashed = pwd_context.hash(plain_pw)

    cur.execute(
        "UPDATE users SET password=%s WHERE user_id=%s;",
        (hashed, user_id)
    )

conn.commit()
cur.close()
conn.close()

print("Migration complete.")