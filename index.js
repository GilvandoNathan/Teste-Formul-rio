const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');
const { createCanvas } = require('canvas');
const { format } = require('date-fns');

const app = express();
app.use(express.urlencoded({ extended: true }));

// Caminho do banco de dados
const DATABASE = path.join(__dirname, '_database.db');

// Conectar ao banco de dados SQLite
const db = new sqlite3.Database(DATABASE, (err) => {
  if (err) {
    console.error('Erro ao conectar ao banco de dados:', err.message);
  } else {
    console.log('Conectado ao banco de dados SQLite.');
  }
});

// Inicializar o banco de dados
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS respostas (
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
    ausencias TEXT
  )`);
});

// Rota inicial
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'form.html'));
});

// Submissão do formulário
app.post('/submit', (req, res) => {
  const {
    data,
    encarregados,
    profissionais_presentes,
    turma,
    turno,
    tema_ddsig,
    atividades_mecanica,
    atividades_eletrica,
    organizacao_limpeza,
    atividades_caldeiraria,
    atividades_transporte,
    atividades_mobilizacao,
    atividades_logistica,
    outras_atividades,
    pendencias,
    ocorrencias_ehs,
    ausencias,
  } = req.body;

  db.run(
    `INSERT INTO respostas (data, encarregados, profissionais_presentes, turma, turno, tema_ddsig, atividades_mecanica, atividades_eletrica, organizacao_limpeza, atividades_caldeiraria, atividades_transporte, atividades_mobilizacao, atividades_logistica, outras_atividades, pendencias, ocorrencias_ehs, ausencias) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [data, encarregados, profissionais_presentes, turma, turno, tema_ddsig, atividades_mecanica, atividades_eletrica, organizacao_limpeza, atividades_caldeiraria, atividades_transporte, atividades_mobilizacao, atividades_logistica, outras_atividades, pendencias, ocorrencias_ehs, ausencias],
    function (err) {
      if (err) {
        console.error('Erro ao inserir dados:', err.message);
      } else {
        console.log(`Uma linha foi inserida com o ID ${this.lastID}`);
        res.redirect('/responses');
      }
    }
  );
});

// Exibição das respostas
app.get('/responses', (req, res) => {
  const encarregadoFilter = req.query.encarregado || 'Todos';

  let query = "SELECT * FROM respostas";
  let params = [];

  if (encarregadoFilter !== 'Todos') {
    query += " WHERE encarregados = ?";
    params.push(encarregadoFilter);
  }

  db.all(query, params, (err, rows) => {
    if (err) {
      console.error('Erro ao recuperar dados:', err.message);
      res.status(500).send('Erro no servidor');
    } else {
      res.json(rows); // Aqui você pode ajustar para renderizar um template HTML
    }
  });
});

// Geração de PDF
app.get('/generate_pdf', (req, res) => {
  const recordId = req.query.id;
  if (!recordId) {
    return res.status(400).send('ID do relatório não fornecido');
  }

  db.get("SELECT * FROM respostas WHERE id = ?", [recordId], (err, row) => {
    if (err) {
      console.error('Erro ao recuperar relatório:', err.message);
      return res.status(500).send('Erro no servidor');
    }

    if (!row) {
      return res.status(404).send('Relatório não encontrado');
    }

    const width = 612;
    const height = 792;
    const canvas = createCanvas(width, height);
    const ctx = canvas.getContext('2d');

    const text = [
      `Data: ${row.data}`,
      `Encarregados: ${row.encarregados}`,
      `Profissionais Presentes: ${row.profissionais_presentes}`,
      `Turma: ${row.turma}`,
      `Turno: ${row.turno}`,
      `Tema do DDSIG: ${row.tema_ddsig}`,
      `Atividades de Mecânica: ${row.atividades_mecanica}`,
      `Atividades de Elétrica: ${row.atividades_eletrica}`,
      `Organização e Limpeza: ${row.organizacao_limpeza}`,
      `Atividades de Caldeiraria: ${row.atividades_caldeiraria}`,
      `Atividades de Transporte: ${row.atividades_transporte}`,
      `Atividades de Mobilização: ${row.atividades_mobilizacao}`,
      `Atividades de Logística: ${row.atividades_logistica}`,
      `Outras Atividades: ${row.outras_atividades}`,
      `Pendências: ${row.pendencias}`,
      `Ocorrências de EHS: ${row.ocorrencias_ehs}`,
      `Ausências: ${row.ausencias}`,
    ];

    let y = 40;
    ctx.font = '16px Arial';
    text.forEach(line => {
      ctx.fillText(line, 40, y);
      y += 24;
    });

    res.setHeader('Content-disposition', 'attachment; filename="report.pdf"');
    res.setHeader('Content-type', 'application/pdf');
    canvas.createPDFStream().pipe(res);
  });
});

// Iniciar o servidor
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});

/* node index.js

http://localhost:3000*/