from database import get_db


def add_student(name, email=None, turma=None):
    with get_db() as conn:
        conn.execute("INSERT INTO students (name, email, turma) VALUES (?, ?, ?)",
                     (name, email or None, turma or None))


def edit_student(student_id, name, email=None, turma=None):
    with get_db() as conn:
        conn.execute("UPDATE students SET name=?, email=?, turma=? WHERE id=?",
                     (name, email or None, turma or None, student_id))


def remove_student(student_id):
    with get_db() as conn:
        conn.execute("DELETE FROM students WHERE id=?", (student_id,))


def list_students():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM students ORDER BY name").fetchall()
        return [dict(r) for r in rows]


def search_students(term):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM students WHERE name LIKE ? OR email LIKE ? ORDER BY name",
                            (f"%{term}%", f"%{term}%")).fetchall()
        return [dict(r) for r in rows]
