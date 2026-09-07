import sqlite3

DB = "telemetry.db"

def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs 
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            uploaded_at TEXT NOT NULL) """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            timestamp_ms INTEGER,
            can_bus INTEGER,
            can_id INTEGER,
            signal_name TEXT,
            value REAL,
            physical_value TEXT,
            FOREIGN KEY (run_id) REFERENCES runs (id)) """)

    conn.commit()
    conn.close()
    print("Database")

if __name__ == "__main__":
    init_db()