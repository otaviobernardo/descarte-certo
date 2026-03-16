# Descarte Certo

Stack: FastAPI + HTML + CSS + JS (sem frameworks)

## Funcionalidades

- Login e Cadastro de usuário
- Solicitação de coleta (com geração de protocolo)
- Histórico de solicitações
- Lista de pontos de descarte de Joinville

## Como rodar

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Acesse: http://localhost:8000

## Estrutura

```
descarte-simples/
├── backend/
│   └── main.py          # FastAPI + SQLite
├── frontend/
│   ├── css/style.css    # Estilos globais
│   ├── js/utils.js      # Funções de sessão
│   └── pages/
│       ├── login.html
│       ├── cadastro.html
│       ├── home.html
│       ├── solicitar_coleta.html
│       └── historico.html
└── requirements.txt
```
