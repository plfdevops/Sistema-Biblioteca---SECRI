import database


class TestInitDb:
    def test_creates_tables(self):
        conn = database.get_connection()
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        names = [t["name"] for t in tables]
        assert "books" in names
        assert "loans" in names
        conn.close()

    def test_idempotent(self):
        database.init_db()
        database.init_db()  # não deve dar erro

    def test_migrations_add_columns(self):
        conn = database.get_connection()
        info = conn.execute("PRAGMA table_info(loans)").fetchall()
        col_names = [c["name"] for c in info]
        assert "email" in col_names
        assert "notified_at" in col_names
        assert "deadline_date" in col_names
        conn.close()

    def test_foreign_keys_on(self):
        conn = database.get_connection()
        fk = conn.execute("PRAGMA foreign_keys").fetchone()
        assert fk[0] == 1
        conn.close()
