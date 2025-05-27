import sqlite3
from models import Projeto, Equipamento, Checklist, ItemChecklist, PlanoAcao

DATABASE_NAME = 'equipment_checklist.db'

def create_tables():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_projeto TEXT UNIQUE NOT NULL,
            nome_projeto TEXT NOT NULL,
            cliente TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER NOT NULL,
            tag TEXT NOT NULL,
            package TEXT NOT NULL,
            UNIQUE (projeto_id, tag),
            FOREIGN KEY (projeto_id) REFERENCES projetos (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checklists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipamento_id INTEGER NOT NULL,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (equipamento_id) REFERENCES equipamentos (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens_checklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            checklist_id INTEGER NOT NULL,
            pergunta TEXT NOT NULL,
            resposta TEXT,
            foto TEXT,
            FOREIGN KEY (checklist_id) REFERENCES checklists (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planos_acao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_checklist_id INTEGER NOT NULL,
            plano TEXT NOT NULL,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_checklist_id) REFERENCES itens_checklist (id)
        )
    ''')

    conn.commit()
    conn.close()

def get_projeto_por_numero(numero_projeto):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, numero_projeto, nome_projeto, cliente FROM projetos WHERE numero_projeto=?", (numero_projeto,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Projeto(*row)
    return None

def criar_projeto(numero_projeto, nome_projeto, cliente):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO projetos (numero_projeto, nome_projeto, cliente) VALUES (?, ?, ?)", (numero_projeto, nome_projeto, cliente))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_equipamento_por_tag_projeto(projeto_id, tag):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, projeto_id, tag, package FROM equipamentos WHERE projeto_id=? AND tag=?", (projeto_id, tag))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Equipamento(*row)
    return None

def criar_equipamento(projeto_id, tag, package):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO equipamentos (projeto_id, tag, package) VALUES (?, ?, ?)", (projeto_id, tag, package))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def criar_checklist(equipamento_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO checklists (equipamento_id) VALUES (?)", (equipamento_id,))
    checklist_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return checklist_id

def adicionar_item_checklist(checklist_id, pergunta):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO itens_checklist (checklist_id, pergunta) VALUES (?, ?)", (checklist_id, pergunta))
    conn.commit()
    conn.close()

def atualizar_item_checklist(item_id, resposta, foto=None):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE itens_checklist SET resposta=?, foto=? WHERE id=?", (resposta, foto, item_id))
    conn.commit()
    conn.close()

def criar_plano_acao(item_checklist_id, plano):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO planos_acao (item_checklist_id, plano) VALUES (?, ?)", (item_checklist_id, plano))
    conn.commit()
    conn.close()

def get_checklist_completo(checklist_id):
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            c.id AS checklist_id,
            e.tag AS equipamento_tag,
            p.numero_projeto,
            p.nome_projeto,
            ic.id AS item_id,
            ic.pergunta,
            ic.resposta,
            ic.foto,
            pa.id AS plano_acao_id,
            pa.plano AS plano_acao_descricao
        FROM checklists c
        JOIN equipamentos e ON c.equipamento_id = e.id
        JOIN projetos p ON e.projeto_id = p.id
        LEFT JOIN itens_checklist ic ON c.id = ic.checklist_id
        LEFT JOIN planos_acao pa ON ic.id = pa.item_checklist_id
        WHERE c.id = ?
    ''', (checklist_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Funções para dashboard (exemplo):
def get_checklists_abertos_por_projeto():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.nome_projeto, COUNT(c.id)
        FROM projetos p
        JOIN equipamentos e ON p.id = e.projeto_id
        JOIN checklists c ON e.id = c.equipamento_id
        LEFT JOIN itens_checklist ic ON c.id = ic.checklist_id
        WHERE ic.resposta IS NULL
        GROUP BY p.nome_projeto
    ''')
    result = cursor.fetchall()
    conn.close()
    return result

def get_checklists_concluidos_por_projeto():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.nome_projeto, COUNT(c.id)
        FROM projetos p
        JOIN equipamentos e ON p.id = e.projeto_id
        JOIN checklists c ON e.id = c.equipamento_id
        LEFT JOIN itens_checklist ic ON c.id = ic.checklist_id
        WHERE ic.resposta IS NOT NULL
        GROUP BY p.nome_projeto
    ''')
    result = cursor.fetchall()
    conn.close()
    return result

def get_planos_acao_por_projeto():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.nome_projeto, COUNT(pa.id)
        FROM projetos p
        JOIN equipamentos e ON p.id = e.projeto_id
        JOIN checklists c ON e.id = c.equipamento_id
        JOIN itens_checklist ic ON c.id = ic.checklist_id
        JOIN planos_acao pa ON ic.id = pa.item_checklist_id
        GROUP BY p.nome_projeto
    ''')
    result = cursor.fetchall()
    conn.close()
    return result

if __name__ == '__main__':
    create_tables()