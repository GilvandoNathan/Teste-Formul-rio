from flask import Flask, request, render_template, g
import sqlite3
import os

app = Flask(__name__)

# Caminho do banco de dados
DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')
def init_db():
    print("Iniciando o banco de dados...")
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS respostas (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          pasta TEXT,
                          encarregados TEXT,
                          turma TEXT,
                          turno TEXT,
                          profissionais_presentes TEXT,
                          tecnico_seguranca TEXT,
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
                          observacoes TEXT,
                          ocorrencias_ehs TEXT,
                          ausencias TEXT)''')
        db.commit()
    print("Banco de dados inicializado.")

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
        cursor.execute('''CREATE TABLE IF NOT EXISTS responses
                          (id INTEGER PRIMARY KEY, date TEXT, supervisor TEXT, team TEXT, shift TEXT, professionals TEXT,
                           safety_technician TEXT, ddsig_theme TEXT, mechanical_activities TEXT, electrical_activities TEXT,
                           cleaning TEXT, boilermaking_activities TEXT, transport_activities TEXT, mobilization_activities TEXT,
                           logistics_activities TEXT, other_activities TEXT, pending_issues TEXT, observations TEXT, ehs_occurences TEXT, absences TEXT)''')
        db.commit()

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    date = request.form['pasta']
    supervisor = request.form['encarregados']
    team = request.form['turma']
    shift = request.form['turno']
    professionals = ','.join(request.form.getlist('edidelson'))
    safety_technician = request.form['ts']
    ddsig_theme = request.form['tdd']
    mechanical_activities = request.form['ame']
    electrical_activities = request.form['ele']
    cleaning = request.form['oli']
    boilermaking_activities = request.form['aca']
    transport_activities = request.form['atr']
    mobilization_activities = request.form['amo']
    logistics_activities = request.form['alo']
    other_activities = request.form['oat']
    pending_issues = request.form['pen']
    observations = request.form['obs']
    ehs_occurences = request.form['oco']
    absences = request.form['aus']

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''INSERT INTO responses (date, supervisor, team, shift, professionals, safety_technician, ddsig_theme, 
                    mechanical_activities, electrical_activities, cleaning, boilermaking_activities, transport_activities, 
                    mobilization_activities, logistics_activities, other_activities, pending_issues, observations, 
                    ehs_occurences, absences) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (date, supervisor, team, shift, professionals, safety_technician, ddsig_theme, mechanical_activities, 
                    electrical_activities, cleaning, boilermaking_activities, transport_activities, mobilization_activities, 
                    logistics_activities, other_activities, pending_issues, observations, ehs_occurences, absences))
    db.commit()

    return 'Resposta recebida!'

@app.route('/responses')
def responses():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM responses")
    rows = cursor.fetchall()

    return render_template('responses.html', rows=rows)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
