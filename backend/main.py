from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path



app = FastAPI(title="Descarte Certo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# Banco de dados

def get_db():
    conn = sqlite3.connect(str(BASE_DIR / "backend" / "database.db"))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS solicitacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            protocolo TEXT UNIQUE NOT NULL,
            usuario_id INTEGER NOT NULL,
            endereco TEXT NOT NULL,
            descricao TEXT NOT NULL,
            status TEXT DEFAULT 'Pendente',
            criado_em TEXT DEFAULT (datetime('now'))
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS denuncias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            protocolo TEXT UNIQUE NOT NULL,
            usuario_id INTEGER NOT NULL,
            endereco TEXT NOT NULL,
            descricao TEXT NOT NULL,
            status TEXT DEFAULT 'Recebida',
            criado_em TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


init_db()


def gerar_protocolo(prefixo="COL"):
    return f"{prefixo}-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"


# Páginas

@app.get("/")
def login_page():
    return FileResponse(str(FRONTEND_DIR / "pages" / "login.html"))

@app.get("/cadastro")
def cadastro_page():
    return FileResponse(str(FRONTEND_DIR / "pages" / "cadastro.html"))

@app.get("/home")
def home_page():
    return FileResponse(str(FRONTEND_DIR / "pages" / "home.html"))

@app.get("/solicitar-coleta")
def coleta_page():
    return FileResponse(str(FRONTEND_DIR / "pages" / "solicitar_coleta.html"))

@app.get("/historico")
def historico_page():
    return FileResponse(str(FRONTEND_DIR / "pages" / "historico.html"))

@app.get("/denuncia")
def denuncia_page():
    return FileResponse(str(FRONTEND_DIR / "pages" / "denuncia.html"))

@app.get("/mapa")
def mapa_page():
    return FileResponse(str(FRONTEND_DIR / "pages" / "mapa.html"))


# APIs

@app.post("/api/cadastro")
def cadastrar(nome: str = Form(...), email: str = Form(...), senha: str = Form(...)):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
            (nome.strip(), email.strip().lower(), senha)
        )
        conn.commit()
        return {"ok": True, "mensagem": "Cadastro realizado!"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    finally:
        conn.close()


@app.post("/api/login")
def login(email: str = Form(...), senha: str = Form(...)):
    conn = get_db()
    user = conn.execute(
        "SELECT id, nome, email FROM usuarios WHERE email=? AND senha=?",
        (email.strip().lower(), senha)
    ).fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
    return {"ok": True, "usuario": {"id": user["id"], "nome": user["nome"], "email": user["email"]}}


@app.post("/api/coleta")
def solicitar_coleta(
    usuario_id: int = Form(...),
    endereco: str = Form(...),
    descricao: str = Form(...)
):
    protocolo = gerar_protocolo("COL")
    conn = get_db()
    conn.execute(
        "INSERT INTO solicitacoes (protocolo, usuario_id, endereco, descricao) VALUES (?, ?, ?, ?)",
        (protocolo, usuario_id, endereco.strip(), descricao.strip())
    )
    conn.commit()
    conn.close()
    return {"ok": True, "protocolo": protocolo}


@app.post("/api/denuncia")
def registrar_denuncia(
    usuario_id: int = Form(...),
    endereco: str = Form(...),
    descricao: str = Form(...)
):
    protocolo = gerar_protocolo("DEN")
    conn = get_db()
    conn.execute(
        "INSERT INTO denuncias (protocolo, usuario_id, endereco, descricao) VALUES (?, ?, ?, ?)",
        (protocolo, usuario_id, endereco.strip(), descricao.strip())
    )
    conn.commit()
    conn.close()
    return {"ok": True, "protocolo": protocolo}


@app.get("/api/historico/{usuario_id}")
def historico(usuario_id: int):
    conn = get_db()
    coletas = conn.execute(
        "SELECT protocolo, endereco, descricao, status, criado_em FROM solicitacoes WHERE usuario_id=? ORDER BY id DESC",
        (usuario_id,)
    ).fetchall()
    denuncias = conn.execute(
        "SELECT protocolo, endereco, descricao, status, criado_em FROM denuncias WHERE usuario_id=? ORDER BY id DESC",
        (usuario_id,)
    ).fetchall()
    conn.close()
    return {
        "solicitacoes": [dict(r) for r in coletas],
        "denuncias": [dict(r) for r in denuncias]
    }
