# Sistema de Biblioteca - SECRI

Sistema de gerenciamento de biblioteca desenvolvido para o projeto de extensão da faculdade. Permite controlar o acervo de livros, empréstimos e devoluções de forma simples e visual.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/Banco-SQLite-green?logo=sqlite&logoColor=white)
![Tkinter](https://img.shields.io/badge/Interface-Tkinter-orange)
![License](https://img.shields.io/badge/Licença-MIT-yellow)

---

## Funcionalidades

- **Cadastro de livros** — título, autor, categoria e ano
- **Remoção de livros** — com confirmação e limpeza do histórico
- **Empréstimo (aluguel)** — registra quem retirou e a data
- **Devolução** — marca a data de retorno automaticamente
- **Busca** — por título, autor ou categoria
- **Detalhes do livro** — duplo clique para ver histórico completo de empréstimos
- **Status visual** — livros disponíveis em verde, alugados em vermelho
- **Barra de status** — contagem total, disponíveis e alugados

---

## Como rodar

### Pré-requisitos

- Python 3.8 ou superior
- Tkinter (já vem instalado com Python no Windows)

### No Windows

```bash
# Clonar o repositório
git clone https://github.com/plfdevops/Sistema-Biblioteca---SECRI.git
cd Sistema-Biblioteca---SECRI

# Executar
python main.py
```

### No Linux

```bash
git clone https://github.com/plfdevops/Sistema-Biblioteca---SECRI.git
cd Sistema-Biblioteca---SECRI

# Instalar tkinter se necessário (Ubuntu/Debian)
sudo apt install python3-tk

# Executar
python3 main.py
```

---

## Gerar executável (.exe) para Windows

```bash
# Executar o script de build
build.bat
```

O executável será gerado em `dist/Biblioteca.exe`. Basta copiar para qualquer PC com Windows e rodar — não precisa instalar Python.

---

## Popular com dados de teste

Para testar o sistema com ~180 livros de exemplo:

```bash
python seed.py
```

Isso cria livros de diversas categorias (Romance, Fantasia, Terror, Ficção Científica, etc.) com alguns já alugados e com histórico de devoluções.

---

## Sobre o banco de dados

O banco `biblioteca.db` é criado automaticamente na primeira vez que o sistema é aberto. Ele fica salvo **na mesma pasta** do programa.

- Cada máquina tem o seu próprio banco — os dados não são compartilhados entre computadores
- Se quiser transferir os dados para outro PC, basta copiar o arquivo `biblioteca.db` junto com o executável
- O arquivo `biblioteca.db` **não sobe pro GitHub** (está no `.gitignore`) — cada instalação começa vazia

---

## Estrutura do projeto

```
├── main.py           # Ponto de entrada da aplicação
├── database.py       # Conexão e criação do banco SQLite
├── services.py       # Lógica de negócio (CRUD, empréstimos)
├── gui/
│   └── app.py        # Interface gráfica (Tkinter)
├── seed.py           # Script para popular o banco com dados de teste
├── build.bat         # Script para gerar .exe (Windows)
├── biblioteca.ico    # Ícone do executável
├── requirements.txt  # Dependências para build
└── .gitignore
```

---

## Tecnologias

| Componente | Tecnologia |
|-----------|-----------|
| Linguagem | Python 3 |
| Interface | Tkinter |
| Banco de dados | SQLite |
| Build | PyInstaller |

---

## Sobre

Desenvolvido para o projeto de extensão **SECRI** como ferramenta de gestão do acervo da biblioteca.
