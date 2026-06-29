from fastmcp import FastMCP
import aiosqlite
import os
import tempfile
import asyncio

TEMP_DIR = tempfile.gettempdir()
DB_PATH = os.path.join(TEMP_DIR, "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

print(f"Database Path: {DB_PATH}")

mcp = FastMCP("Expense Tracker")

async def init_db():
    try :
        async with aiosqlite.connect(DB_PATH) as c:
            await c.execute("PRAGMA journal_mode=WAL")
            await c.execute("""
                CREATE TABLE IF NOT EXISTS expenses(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    note TEXT DEFAULT ''
                    )
            """)
            await c.execute("INSERT OR IGNORE INTO expenses(date, amount, category) VALUES ('2000-01-01',1000,'food')")
            await c.execute("DELETE FROM expenses WHERE category='test'")
            print("Database initialized successfully with write access")
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise

asyncio.run(init_db())

@mcp.tool
async def add_expense(date: str, amount: float, category: str, subcategory: str = "", note: str = ""):
    """Add a new expense entry to the database"""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute(
                "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
                (date, amount, category, subcategory, note)
            )
            expense_id = cur.lastrowid
            await c.commit()
            return {"status": "success", "id": expense_id, "message":"Expense added Successfully"}
    except Exception as e:
        if "readonly" in str(e).lower():
            return {"status":"error","message":"Database is in read only mode. Check file permissions."}
        return {"status":"error","message":f"Database Error: {str(e)}"}
    
@mcp.tool
async def list_expenses(start_date: str, end_date: str):
    """List all expenses from the database within an inclusive range"""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            cur = await c.execute("SELECT id, date, amount, category, subcategory, note FROM expenses WHERE date between ? and ? ORDER by id ASC", (start_date, end_date))
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in await cur.fetchall()]
    except Exception as e:
        return {"status":"error", "message":f"Error loading expenses: {str(e)}"}
    
@mcp.tool
async def summarize(start_date: str, end_date: str, category: str = None):
    """Summarize expenses by category on the basis of the date range"""
    try:
        async with aiosqlite.connect(DB_PATH) as c:
            query = (
                """
                SELECT category, SUM(amount) as Total_amount
                FROM expenses
                WHERE date between ? and ?
                """
            )
            params = [start_date, end_date]

            if category:
                query += " AND category = ?"
                params.append(category)
            query += " GROUP BY category ORDER BY category ASC"

            cur = await c.execute(query, params)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in await cur.fetchall()]
    except Exception as e:
        return {"status":"error","message":f"Error summarizing expenses: {str(e)}"}
    
@mcp.resource("expense://categories", mime_type="application/json")
def resources():
    """Read Fresh each time so you can edit the file without restarting"""
    with open(CATEGORIES_PATH, 'r', encoding="utf-8") as f:
        return f.read()
    
if __name__ == '__main__': 
    mcp.run()
