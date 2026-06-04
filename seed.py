from database import init_db, get_connection
from datetime import date, timedelta
import random

BOOKS = [
    ("Dom Casmurro", "Machado de Assis", "Romance", 1899),
    ("Memórias Póstumas de Brás Cubas", "Machado de Assis", "Romance", 1881),
    ("O Alienista", "Machado de Assis", "Conto", 1882),
    ("Quincas Borba", "Machado de Assis", "Romance", 1891),
    ("Grande Sertão: Veredas", "Guimarães Rosa", "Romance", 1956),
    ("Vidas Secas", "Graciliano Ramos", "Romance", 1938),
    ("São Bernardo", "Graciliano Ramos", "Romance", 1934),
    ("Capitães da Areia", "Jorge Amado", "Romance", 1937),
    ("Gabriela, Cravo e Canela", "Jorge Amado", "Romance", 1958),
    ("O Cortiço", "Aluísio Azevedo", "Romance", 1890),
    ("Iracema", "José de Alencar", "Romance", 1865),
    ("O Guarani", "José de Alencar", "Romance", 1857),
    ("A Moreninha", "Joaquim Manuel de Macedo", "Romance", 1844),
    ("O Tempo e o Vento", "Erico Verissimo", "Romance", 1949),
    ("Macunaíma", "Mário de Andrade", "Romance", 1928),
    ("A Hora da Estrela", "Clarice Lispector", "Romance", 1977),
    ("Perto do Coração Selvagem", "Clarice Lispector", "Romance", 1943),
    ("Laços de Família", "Clarice Lispector", "Conto", 1960),
    ("O Quinze", "Rachel de Queiroz", "Romance", 1930),
    ("Menino de Engenho", "José Lins do Rego", "Romance", 1932),
    ("Fogo Morto", "José Lins do Rego", "Romance", 1943),
    ("Auto da Compadecida", "Ariano Suassuna", "Teatro", 1955),
    ("O Romance d'A Pedra do Reino", "Ariano Suassuna", "Romance", 1971),
    ("Sagarana", "Guimarães Rosa", "Conto", 1946),
    ("Primeiras Estórias", "Guimarães Rosa", "Conto", 1962),
    ("1984", "George Orwell", "Ficção Científica", 1949),
    ("A Revolução dos Bichos", "George Orwell", "Fábula", 1945),
    ("O Senhor dos Anéis", "J.R.R. Tolkien", "Fantasia", 1954),
    ("O Hobbit", "J.R.R. Tolkien", "Fantasia", 1937),
    ("Harry Potter e a Pedra Filosofal", "J.K. Rowling", "Fantasia", 1997),
    ("Harry Potter e a Câmara Secreta", "J.K. Rowling", "Fantasia", 1998),
    ("Harry Potter e o Prisioneiro de Azkaban", "J.K. Rowling", "Fantasia", 1999),
    ("Harry Potter e o Cálice de Fogo", "J.K. Rowling", "Fantasia", 2000),
    ("Harry Potter e a Ordem da Fênix", "J.K. Rowling", "Fantasia", 2003),
    ("Cem Anos de Solidão", "Gabriel García Márquez", "Realismo Mágico", 1967),
    ("O Amor nos Tempos do Cólera", "Gabriel García Márquez", "Romance", 1985),
    ("Crime e Castigo", "Fiódor Dostoiévski", "Romance", 1866),
    ("Os Irmãos Karamázov", "Fiódor Dostoiévski", "Romance", 1880),
    ("O Idiota", "Fiódor Dostoiévski", "Romance", 1869),
    ("Guerra e Paz", "Liev Tolstói", "Romance", 1869),
    ("Anna Kariênina", "Liev Tolstói", "Romance", 1877),
    ("O Processo", "Franz Kafka", "Romance", 1925),
    ("A Metamorfose", "Franz Kafka", "Novela", 1915),
    ("O Estrangeiro", "Albert Camus", "Romance", 1942),
    ("A Peste", "Albert Camus", "Romance", 1947),
    ("O Pequeno Príncipe", "Antoine de Saint-Exupéry", "Infantil", 1943),
    ("Don Quixote", "Miguel de Cervantes", "Romance", 1605),
    ("Orgulho e Preconceito", "Jane Austen", "Romance", 1813),
    ("Jane Eyre", "Charlotte Brontë", "Romance", 1847),
    ("O Morro dos Ventos Uivantes", "Emily Brontë", "Romance", 1847),
    ("Drácula", "Bram Stoker", "Terror", 1897),
    ("Frankenstein", "Mary Shelley", "Terror", 1818),
    ("Moby Dick", "Herman Melville", "Aventura", 1851),
    ("As Aventuras de Tom Sawyer", "Mark Twain", "Aventura", 1876),
    ("O Grande Gatsby", "F. Scott Fitzgerald", "Romance", 1925),
    ("O Apanhador no Campo de Centeio", "J.D. Salinger", "Romance", 1951),
    ("Para Matar um Rouxinol", "Harper Lee", "Romance", 1960),
    ("A Menina que Roubava Livros", "Markus Zusak", "Romance", 2005),
    ("O Nome da Rosa", "Umberto Eco", "Mistério", 1980),
    ("O Código Da Vinci", "Dan Brown", "Suspense", 2003),
    ("Anjos e Demônios", "Dan Brown", "Suspense", 2000),
    ("Inferno", "Dan Brown", "Suspense", 2013),
    ("O Alquimista", "Paulo Coelho", "Romance", 1988),
    ("Brida", "Paulo Coelho", "Romance", 1990),
    ("Ensaio sobre a Cegueira", "José Saramago", "Romance", 1995),
    ("Memorial do Convento", "José Saramago", "Romance", 1982),
    ("As Intermitências da Morte", "José Saramago", "Romance", 2005),
    ("A Insustentável Leveza do Ser", "Milan Kundera", "Romance", 1984),
    ("Admirável Mundo Novo", "Aldous Huxley", "Ficção Científica", 1932),
    ("Fahrenheit 451", "Ray Bradbury", "Ficção Científica", 1953),
    ("Crônica de uma Morte Anunciada", "Gabriel García Márquez", "Novela", 1981),
    ("O Velho e o Mar", "Ernest Hemingway", "Novela", 1952),
    ("Por Quem os Sinos Dobram", "Ernest Hemingway", "Romance", 1940),
    ("A Arte da Guerra", "Sun Tzu", "Filosofia", -500),
    ("O Príncipe", "Nicolau Maquiavel", "Filosofia", 1532),
    ("Sapiens", "Yuval Noah Harari", "Não-ficção", 2011),
    ("Homo Deus", "Yuval Noah Harari", "Não-ficção", 2015),
    ("21 Lições para o Século 21", "Yuval Noah Harari", "Não-ficção", 2018),
    ("O Poder do Hábito", "Charles Duhigg", "Não-ficção", 2012),
    ("Rápido e Devagar", "Daniel Kahneman", "Não-ficção", 2011),
    ("Pai Rico, Pai Pobre", "Robert Kiyosaki", "Finanças", 1997),
    ("A Sutil Arte de Ligar o F*da-se", "Mark Manson", "Autoajuda", 2016),
    ("O Mundo de Sofia", "Jostein Gaarder", "Filosofia", 1991),
    ("It: A Coisa", "Stephen King", "Terror", 1986),
    ("O Iluminado", "Stephen King", "Terror", 1977),
    ("Carrie, a Estranha", "Stephen King", "Terror", 1974),
    ("Misery", "Stephen King", "Terror", 1987),
    ("Fundação", "Isaac Asimov", "Ficção Científica", 1951),
    ("Eu, Robô", "Isaac Asimov", "Ficção Científica", 1950),
    ("Neuromancer", "William Gibson", "Ficção Científica", 1984),
    ("Duna", "Frank Herbert", "Ficção Científica", 1965),
    ("O Guia do Mochileiro das Galáxias", "Douglas Adams", "Ficção Científica", 1979),
    ("Contato", "Carl Sagan", "Ficção Científica", 1985),
    ("Cosmos", "Carl Sagan", "Não-ficção", 1980),
    ("Uma Breve História do Tempo", "Stephen Hawking", "Não-ficção", 1988),
    ("O Universo numa Casca de Noz", "Stephen Hawking", "Não-ficção", 2001),
    ("A Elegância do Ouriço", "Muriel Barbery", "Romance", 2006),
    ("O Caçador de Pipas", "Khaled Hosseini", "Romance", 2003),
    ("A Cidade do Sol", "Khaled Hosseini", "Romance", 2007),
    ("Middlesex", "Jeffrey Eugenides", "Romance", 2002),
    ("As Virgens Suicidas", "Jeffrey Eugenides", "Romance", 1993),
    ("Laranja Mecânica", "Anthony Burgess", "Ficção Científica", 1962),
    ("Trainspotting", "Irvine Welsh", "Romance", 1993),
    ("Na Estrada", "Jack Kerouac", "Romance", 1957),
    ("O Lobo da Estepe", "Hermann Hesse", "Romance", 1927),
    ("Sidarta", "Hermann Hesse", "Romance", 1922),
    ("Demian", "Hermann Hesse", "Romance", 1919),
    ("O Jogo das Contas de Vidro", "Hermann Hesse", "Romance", 1943),
    ("Cem Sonetos de Amor", "Pablo Neruda", "Poesia", 1959),
    ("O Diário de Anne Frank", "Anne Frank", "Biografia", 1947),
    ("A Culpa é das Estrelas", "John Green", "Romance", 2012),
    ("Cidades de Papel", "John Green", "Romance", 2008),
    ("O Teorema Katherine", "John Green", "Romance", 2006),
    ("Divergente", "Veronica Roth", "Ficção Científica", 2011),
    ("Insurgente", "Veronica Roth", "Ficção Científica", 2012),
    ("Convergente", "Veronica Roth", "Ficção Científica", 2013),
    ("Jogos Vorazes", "Suzanne Collins", "Ficção Científica", 2008),
    ("Em Chamas", "Suzanne Collins", "Ficção Científica", 2009),
    ("A Esperança", "Suzanne Collins", "Ficção Científica", 2010),
    ("Percy Jackson e o Ladrão de Raios", "Rick Riordan", "Fantasia", 2005),
    ("Percy Jackson e o Mar de Monstros", "Rick Riordan", "Fantasia", 2006),
    ("Eragon", "Christopher Paolini", "Fantasia", 2003),
    ("As Crônicas de Nárnia", "C.S. Lewis", "Fantasia", 1950),
    ("O Conde de Monte Cristo", "Alexandre Dumas", "Aventura", 1844),
    ("Os Três Mosqueteiros", "Alexandre Dumas", "Aventura", 1844),
    ("Os Miseráveis", "Victor Hugo", "Romance", 1862),
    ("O Corcunda de Notre-Dame", "Victor Hugo", "Romance", 1831),
    ("Vinte Mil Léguas Submarinas", "Júlio Verne", "Aventura", 1870),
    ("A Volta ao Mundo em 80 Dias", "Júlio Verne", "Aventura", 1873),
    ("Viagem ao Centro da Terra", "Júlio Verne", "Aventura", 1864),
    ("Robinson Crusoé", "Daniel Defoe", "Aventura", 1719),
    ("A Ilha do Tesouro", "Robert Louis Stevenson", "Aventura", 1883),
    ("O Retrato de Dorian Gray", "Oscar Wilde", "Romance", 1890),
    ("Sherlock Holmes: Um Estudo em Vermelho", "Arthur Conan Doyle", "Mistério", 1887),
    ("Sherlock Holmes: O Cão dos Baskervilles", "Arthur Conan Doyle", "Mistério", 1902),
    ("O Chamado de Cthulhu", "H.P. Lovecraft", "Terror", 1928),
    ("Nas Montanhas da Loucura", "H.P. Lovecraft", "Terror", 1936),
    ("Crônicas Marcianas", "Ray Bradbury", "Ficção Científica", 1950),
    ("2001: Uma Odisseia no Espaço", "Arthur C. Clarke", "Ficção Científica", 1968),
    ("Solaris", "Stanislaw Lem", "Ficção Científica", 1961),
    ("O Fim da Eternidade", "Isaac Asimov", "Ficção Científica", 1955),
    ("Flores para Algernon", "Daniel Keyes", "Ficção Científica", 1966),
    ("Matadouro-Cinco", "Kurt Vonnegut", "Ficção Científica", 1969),
    ("O Senhor das Moscas", "William Golding", "Romance", 1954),
    ("A Casa dos Espíritos", "Isabel Allende", "Realismo Mágico", 1982),
    ("Como Água para Chocolate", "Laura Esquivel", "Realismo Mágico", 1989),
    ("O Labirinto dos Espíritos", "Carlos Ruiz Zafón", "Mistério", 2016),
    ("A Sombra do Vento", "Carlos Ruiz Zafón", "Mistério", 2001),
    ("O Jogo do Anjo", "Carlos Ruiz Zafón", "Mistério", 2008),
    ("Rayuela", "Julio Cortázar", "Romance", 1963),
    ("Ficções", "Jorge Luis Borges", "Conto", 1944),
    ("O Aleph", "Jorge Luis Borges", "Conto", 1949),
    ("Pedro Páramo", "Juan Rulfo", "Realismo Mágico", 1955),
    ("O Túnel", "Ernesto Sabato", "Romance", 1948),
    ("Sobre Heróis e Tumbas", "Ernesto Sabato", "Romance", 1961),
    ("A Invenção de Morel", "Adolfo Bioy Casares", "Ficção Científica", 1940),
    ("O Evangelho Segundo Jesus Cristo", "José Saramago", "Romance", 1991),
    ("Todos os Nomes", "José Saramago", "Romance", 1997),
    ("Budapeste", "Chico Buarque", "Romance", 2003),
    ("Leite Derramado", "Chico Buarque", "Romance", 2009),
    ("Dois Irmãos", "Milton Hatoum", "Romance", 2000),
    ("Relato de um Certo Oriente", "Milton Hatoum", "Romance", 1989),
    ("Cidade de Deus", "Paulo Lins", "Romance", 1997),
    ("Extraordinário", "R.J. Palacio", "Romance", 2012),
    ("Persuasão", "Jane Austen", "Romance", 1817),
    ("Razão e Sensibilidade", "Jane Austen", "Romance", 1811),
    ("Silmarillion", "J.R.R. Tolkien", "Fantasia", 1977),
    ("O Nome do Vento", "Patrick Rothfuss", "Fantasia", 2007),
    ("O Temor do Sábio", "Patrick Rothfuss", "Fantasia", 2011),
    ("Mistborn: O Império Final", "Brandon Sanderson", "Fantasia", 2006),
    ("O Caminho dos Reis", "Brandon Sanderson", "Fantasia", 2010),
    ("Se um Viajante numa Noite de Inverno", "Italo Calvino", "Romance", 1979),
    ("As Cidades Invisíveis", "Italo Calvino", "Romance", 1972),
    ("O Barão nas Árvores", "Italo Calvino", "Romance", 1957),
    ("Norwegian Wood", "Haruki Murakami", "Romance", 1987),
    ("Kafka à Beira-Mar", "Haruki Murakami", "Romance", 2002),
    ("1Q84", "Haruki Murakami", "Romance", 2009),
    ("O Perfume", "Patrick Süskind", "Romance", 1985),
    ("Se Isso é um Homem", "Primo Levi", "Biografia", 1947),
    ("A Trégua", "Primo Levi", "Biografia", 1963),
    ("O Leopardo", "Giuseppe Tomasi di Lampedusa", "Romance", 1958),
    ("Deserto dos Tártaros", "Dino Buzzati", "Romance", 1940),
]

PEOPLE = [
    "Ana Silva", "Carlos Oliveira", "Maria Santos", "Joao Pereira",
    "Fernanda Costa", "Pedro Souza", "Juliana Lima", "Rafael Almeida",
    "Beatriz Ferreira", "Lucas Rodrigues", "Camila Martins", "Bruno Araujo",
    "Larissa Gomes", "Thiago Ribeiro", "Amanda Carvalho",
]


def populate():
    init_db()
    conn = get_connection()

    conn.execute("DELETE FROM loans")
    conn.execute("DELETE FROM books")
    conn.commit()

    for i, (title, author, category, year) in enumerate(BOOKS, start=1):
        code = f"{i:03d}"
        conn.execute(
            "INSERT INTO books (title, author, category, year, code) VALUES (?, ?, ?, ?, ?)",
            (title, author, category, year, code),
        )
    conn.commit()

    books = conn.execute("SELECT id FROM books").fetchall()
    loaned = random.sample(books, 30)

    for book in loaned[:10]:
        person = random.choice(PEOPLE)
        days_ago = random.randint(15, 40)
        loan_date = (date.today() - timedelta(days=days_ago)).isoformat()
        deadline_date = (date.today() - timedelta(days=random.randint(1, 10))).isoformat()
        conn.execute(
            "INSERT INTO loans (book_id, person, loan_date, deadline_date) VALUES (?, ?, ?, ?)",
            (book["id"], person, loan_date, deadline_date),
        )
        conn.execute("UPDATE books SET available = 0 WHERE id = ?", (book["id"],))

    for book in loaned[10:20]:
        person = random.choice(PEOPLE)
        days_ago = random.randint(1, 3)
        loan_date = (date.today() - timedelta(days=days_ago)).isoformat()
        deadline_date = (date.today() + timedelta(days=random.randint(7, 30))).isoformat()
        conn.execute(
            "INSERT INTO loans (book_id, person, loan_date, deadline_date) VALUES (?, ?, ?, ?)",
            (book["id"], person, loan_date, deadline_date),
        )
        conn.execute("UPDATE books SET available = 0 WHERE id = ?", (book["id"],))

    for book in loaned[20:]:
        person = random.choice(PEOPLE)
        days_ago = random.randint(1, 20)
        loan_date = (date.today() - timedelta(days=days_ago)).isoformat()
        conn.execute(
            "INSERT INTO loans (book_id, person, loan_date) VALUES (?, ?, ?)",
            (book["id"], person, loan_date),
        )
        conn.execute("UPDATE books SET available = 0 WHERE id = ?", (book["id"],))

    available = conn.execute("SELECT id FROM books WHERE available = 1").fetchall()
    history_books = random.sample(available, 50)
    for book in history_books:
        person = random.choice(PEOPLE)
        days_loan = random.randint(30, 90)
        days_return = random.randint(1, 29)
        loan_date = (date.today() - timedelta(days=days_loan)).isoformat()
        return_date = (date.today() - timedelta(days=days_return)).isoformat()
        conn.execute(
            "INSERT INTO loans (book_id, person, loan_date, return_date) VALUES (?, ?, ?, ?)",
            (book["id"], person, loan_date, return_date),
        )

    conn.commit()
    total = conn.execute("SELECT COUNT(*) as c FROM books").fetchone()["c"]
    loaned_count = conn.execute("SELECT COUNT(*) as c FROM books WHERE available = 0").fetchone()["c"]
    conn.close()
    print(f"Done: {total} books ({loaned_count} loaned)")


if __name__ == "__main__":
    populate()
