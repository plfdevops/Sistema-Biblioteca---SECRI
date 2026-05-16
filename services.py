from database import get_connection
from datetime import date


def adicionar_livro(titulo, autor, categoria=None, ano=None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO livros (titulo, autor, categoria, ano) VALUES (?, ?, ?, ?)",
        (titulo, autor, categoria or None, ano or None),
    )
    conn.commit()
    conn.close()


def remover_livro(livro_id):
    conn = get_connection()
    conn.execute("DELETE FROM emprestimos WHERE livro_id = ?", (livro_id,))
    conn.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
    conn.commit()
    conn.close()


def alugar_livro(livro_id, pessoa):
    conn = get_connection()
    livro = conn.execute("SELECT disponivel FROM livros WHERE id = ?", (livro_id,)).fetchone()
    if not livro:
        conn.close()
        raise ValueError("Livro não encontrado")
    if not livro["disponivel"]:
        conn.close()
        raise ValueError("Livro já está alugado")
    conn.execute(
        "INSERT INTO emprestimos (livro_id, pessoa, data_retirada) VALUES (?, ?, ?)",
        (livro_id, pessoa, date.today().isoformat()),
    )
    conn.execute("UPDATE livros SET disponivel = 0 WHERE id = ?", (livro_id,))
    conn.commit()
    conn.close()


def devolver_livro(livro_id):
    conn = get_connection()
    conn.execute(
        "UPDATE emprestimos SET data_devolucao = ? WHERE livro_id = ? AND data_devolucao IS NULL",
        (date.today().isoformat(), livro_id),
    )
    conn.execute("UPDATE livros SET disponivel = 1 WHERE id = ?", (livro_id,))
    conn.commit()
    conn.close()


def listar_livros():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM livros ORDER BY titulo").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def buscar_livros(termo):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM livros WHERE titulo LIKE ? OR autor LIKE ? OR categoria LIKE ? ORDER BY titulo",
        (f"%{termo}%", f"%{termo}%", f"%{termo}%"),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def historico_emprestimos(livro_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM emprestimos WHERE livro_id = ? ORDER BY data_retirada DESC",
        (livro_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
