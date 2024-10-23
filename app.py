from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime, timedelta
import random
import string

app = Flask(__name__)
app.secret_key = '123'  # Chave secreta para as sessões

# Função para gerar um código de acompanhamento alfanumérico de 5 dígitos
def gerar_codigo_acompanhamento():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=5))

# Função para calcular o status e a duração do processo com base no valor do projeto
def calcular_status(valor_projeto):
    if valor_projeto > 4_800_000:  # Central Grande
        return 'central grande', 60
    else:  # Central Pequena
        return 'central pequena', 40

# Página de login para analistas e clientes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        tipo_usuario = request.form['tipo_usuario']

        # Verificação simples de login
        if tipo_usuario == 'analista' and usuario == 'analista' and senha == 'senha':
            session['usuario'] = 'analista'
            return redirect(url_for('cadastro'))  # Redireciona para a página de cadastro
        elif tipo_usuario == 'cliente':
            session['usuario'] = 'cliente'
            return redirect(url_for('consulta_projeto'))  # Redireciona para a página de consulta
        else:
            return render_template('erro.html', mensagem="Usuário ou senha inválidos.")
    
    return render_template('login.html')  # Renderiza o template de login no GET


# Página de cadastro de novos projetos (acessível apenas para analistas)
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if 'usuario' not in session or session['usuario'] != 'analista':
        return redirect(url_for('login'))  # Redireciona para o login se não for analista

    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        valor_projeto = float(request.form['valor_projeto'])
        data_inicio = datetime.now()
        status, dias = calcular_status(valor_projeto)

        # Gerar o código de acompanhamento
        codigo_acompanhamento = gerar_codigo_acompanhamento()

        # Calcular data de término (incluindo os 20 dias da agência)
        data_fim = data_inicio + timedelta(days=dias + 20)

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('''INSERT INTO projetos (nome_cliente, valor_projeto, status, data_inicio, data_fim, codigo_acompanhamento)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (nome_cliente, valor_projeto, status, data_inicio.strftime('%Y-%m-%d'), data_fim.strftime('%Y-%m-%d'), codigo_acompanhamento))

        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    
    return render_template('cadastro.html')

# Página inicial
@app.route('/')
def index():
    return render_template('login.html')

# Consulta de projetos para clientes
@app.route('/consulta', methods=['GET', 'POST'])
def consulta_projeto():
    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Inclui o código de acompanhamento na consulta
        cursor.execute("SELECT nome_cliente, valor_projeto, status, data_inicio, data_fim, codigo_acompanhamento FROM projetos WHERE nome_cliente=?", (nome_cliente,))
        projeto = cursor.fetchone()
        conn.close()

        if projeto:
            return render_template('resultado.html', projeto=projeto)
        else:
            return render_template('erro.html', mensagem="Projeto não encontrado.")
    
    return render_template('consulta.html')  # Renderiza consulta.html para o método GET

# Página de erro (caso haja problemas no login ou consulta)
@app.route('/erro')
def erro():
    return render_template('erro.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
