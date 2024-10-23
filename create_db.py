import sqlite3

def create_database():
    conn = sqlite3.connect('database.db')  # Conecte ao arquivo database.db
    cursor = conn.cursor()

    # Cria a tabela 'projetos' se ela não existir
    cursor.execute('''CREATE TABLE IF NOT EXISTS projetos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_cliente TEXT NOT NULL,
                    valor_projeto REAL NOT NULL,
                    status TEXT NOT NULL,
                    data_inicio TEXT NOT NULL,
                    data_fim TEXT,
                    codigo_acompanhamento TEXT NOT NULL UNIQUE)''')


    conn.commit()  # Confirma as alterações
    conn.close()   # Fecha a conexão

create_database()
