import aiosqlite

DB_FILE = "bot_data.db"

async def init_db():
    """Initialize the database and create the users table if it doesn't exist."""
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        await db.commit()


async def add_user(chat_id: int, name: str):
    """Add a user only if they are not already in the database."""
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute("SELECT chat_id FROM users WHERE chat_id = ?", (chat_id,))
        existing = await cursor.fetchone()
        if existing:
            return False  # User already exists
        await db.execute("INSERT INTO users (chat_id, name) VALUES (?, ?)", (chat_id, name))
        await db.commit()
        return True


async def get_all_users():
    """Return a list of all user names."""
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute("SELECT name FROM users")
        rows = await cursor.fetchall()
        return [row[0] for row in rows] if rows else []
