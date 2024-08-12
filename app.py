from flask import Flask, request, render_template, g, send_file
import sqlite3
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

# Caminho do banco de dados
DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), '_database.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS respostas (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          data TEXT,
                          encarregados TEXT,
                          profissionais_presentes TEXT,
                          turma TEXT,
                          turno TEXT,
                          tema_ddsig TEXT,
                          atividades_mecanica TEXT,
                          atividades_eletrica TEXT,
                          organizacao_limpeza TEXT,
                          atividades_caldeiraria TEXT,
                          atividades_transporte TEXT,
                          atividades_mobilizacao TEXT,
                          atividades_logistica TEXT,
                          outras_atividades TEXT,
                          pendencias TEXT,
                          ocorrencias_ehs TEXT,
                          ausencias TEXT)''')
        db.commit()
        
@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.get('data', '')  # Adicionando valor padrão
    encarregados = request.form.get('encarregados', '')  # Adicionando valor padrão
    profissionais_presentes = request.form.get('profissionais_presentes', '')
    turma = request.form.get('turma', '')  # Adicionando valor padrão
    turno = request.form.get('turno', '')  # Adicionando valor padrão
    tema_ddsig = request.form.get('tema_ddsig', '')
    atividades_mecanica = request.form.get('atividades_mecanica', '')
    atividades_eletrica = request.form.get('atividades_eletrica', '')
    organizacao_limpeza = request.form.get('organizacao_limpeza', '')
    atividades_caldeiraria = request.form.get('atividades_caldeiraria', '')
    atividades_transporte = request.form.get('atividades_transporte', '')
    atividades_mobilizacao = request.form.get('atividades_mobilizacao', '')
    atividades_logistica = request.form.get('atividades_logistica', '')
    outras_atividades = request.form.get('outras_atividades', '')
    pendencias = request.form.get('pendencias', '')
    ocorrencias_ehs = request.form.get('ocorrencias_ehs', '')
    ausencias = request.form.get('ausencias', '')

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''INSERT INTO respostas 
                      (data, encarregados, profissionais_presentes, turma, turno, tema_ddsig, atividades_mecanica, atividades_eletrica, 
                      organizacao_limpeza, atividades_caldeiraria, atividades_transporte, atividades_mobilizacao, atividades_logistica, 
                      outras_atividades, pendencias, ocorrencias_ehs, ausencias) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (data, encarregados, profissionais_presentes, turma, turno, tema_ddsig, atividades_mecanica, atividades_eletrica, 
                    organizacao_limpeza, atividades_caldeiraria, atividades_transporte, atividades_mobilizacao, atividades_logistica, 
                    outras_atividades, pendencias, ocorrencias_ehs, ausencias))
    db.commit()

    return 'Resposta recebida!'

@app.route('/responses', methods=['GET'])
def responses():
    encarregado_filter = request.args.get('encarregado', 'Todos')

    db = get_db()
    cursor = db.cursor()

    if encarregado_filter == 'Todos':
        cursor.execute("SELECT * FROM respostas")
    else:
        cursor.execute("SELECT * FROM respostas WHERE encarregados = ?", (encarregado_filter,))
    
    rows = cursor.fetchall()

    return render_template('responses.html', rows=rows, selected_encarregado=encarregado_filter)

@app.route('/generate_pdf', methods=['GET'])
def generate_pdf():
    record_id = request.args.get('id')
    if not record_id:
        return 'ID do relatório não fornecido', 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM respostas WHERE id = ?", (record_id,))
    row = cursor.fetchone()

    if not row:
        return 'Relatório não encontrado', 404

    output = BytesIO()
    c = canvas.Canvas(output, pagesize=letter)
    width, height = letter

    # Dados do relatório
    text = [
        f"Data: {row[1]}",
        f"Encarregados: {row[2]}",
        f"Profissionais Presentes: {row[3]}",
        f"Turma: {row[4]}",
        f"Turno: {row[5]}",
        f"Tema do DDSIG: {row[6]}",
        f"Atividades de Mecânica: {row[7]}",
        f"Atividades de Elétrica: {row[8]}",
        f"Organização e Limpeza: {row[9]}",
        f"Atividades de Caldeiraria: {row[10]}",
        f"Atividades de Transporte: {row[11]}",
        f"Atividades de Mobilização: {row[12]}",
        f"Atividades de Logística: {row[13]}",
        f"Outras Atividades: {row[14]}",
        f"Pendências: {row[15]}",
        f"Ocorrências de EHS: {row[16]}",
        f"Ausências: {row[17]}",
    ]

    y = height - 40
    for line in text:
        c.drawString(40, y, line)
        y -= 20

    c.save()
    output.seek(0)
    
    return send_file(output, as_attachment=True, download_name='relatorio.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
