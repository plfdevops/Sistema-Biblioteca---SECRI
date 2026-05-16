from database import get_connection
from datetime import date, timedelta


def adicionar_livro(titulo, autor, categoria=None, ano=None, codigo=None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO livros (titulo, autor, categoria, ano, codigo) VALUES (?, ?, ?, ?, ?)",
        (titulo, autor, categoria or None, ano or None, codigo or None),
    )
    conn.commit()
    conn.close()


def remover_livro(livro_id):
    conn = get_connection()
    conn.execute("DELETE FROM emprestimos WHERE livro_id = ?", (livro_id,))
    conn.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
    conn.commit()
    conn.close()


def editar_livro(livro_id, titulo, autor, categoria=None, ano=None, codigo=None):
    conn = get_connection()
    conn.execute(
        "UPDATE livros SET titulo = ?, autor = ?, categoria = ?, ano = ?, codigo = ? WHERE id = ?",
        (titulo, autor, categoria or None, ano or None, codigo or None, livro_id),
    )
    conn.commit()
    conn.close()


def obter_livro(livro_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM livros WHERE id = ?", (livro_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def alugar_livro(livro_id, pessoa, prazo_dias=None):
    conn = get_connection()
    livro = conn.execute("SELECT disponivel FROM livros WHERE id = ?", (livro_id,)).fetchone()
    if not livro:
        conn.close()
        raise ValueError("Livro não encontrado")
    if not livro["disponivel"]:
        conn.close()
        raise ValueError("Livro já está alugado")
    conn.execute(
        "INSERT INTO emprestimos (livro_id, pessoa, data_retirada, prazo_dias) VALUES (?, ?, ?, ?)",
        (livro_id, pessoa, date.today().isoformat(), prazo_dias),
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


def filtrar_por_categoria(categoria):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM livros WHERE categoria = ? ORDER BY titulo", (categoria,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def listar_categorias():
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT categoria FROM livros WHERE categoria IS NOT NULL ORDER BY categoria").fetchall()
    conn.close()
    return [r["categoria"] for r in rows]


def historico_emprestimos(livro_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM emprestimos WHERE livro_id = ? ORDER BY data_retirada DESC",
        (livro_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def emprestimo_ativo(livro_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM emprestimos WHERE livro_id = ? AND data_devolucao IS NULL",
        (livro_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def esta_atrasado(livro_id):
    emp = emprestimo_ativo(livro_id)
    if not emp or not emp["prazo_dias"]:
        return False
    data_ret = date.fromisoformat(emp["data_retirada"])
    data_limite = data_ret + timedelta(days=emp["prazo_dias"])
    return date.today() > data_limite
