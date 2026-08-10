"""
criar_admin.py
-----------------------------------------------------------------------------
Script para criar o primeiro usuário administrador do sistema.
Rode isso apenas UMA VEZ (ou sempre que precisar adicionar um admin).

IMPORTANTE: antes de rodar este script, crie o banco de dados vazio
chamado 'ong_sistema' no phpMyAdmin (Novo > nome: ong_sistema > Criar).
O Flask/SQLAlchemy cria as TABELAS sozinho, mas não cria o banco em si.

Como usar:
    python criar_admin.py
-----------------------------------------------------------------------------
"""

import getpass
from app import app
from models import db, Usuario

with app.app_context():
    print("=== Criar novo usuário administrador ===")
    nome = input("Nome: ").strip()
    email = input("Email: ").strip().lower()
    senha = getpass.getpass("Senha: ")

    if Usuario.query.filter_by(email=email).first():
        print(f"\nJá existe um usuário cadastrado com o email '{email}'.")
    else:
        usuario = Usuario(nome=nome, email=email, tipo='admin')
        usuario.set_senha(senha)
        db.session.add(usuario)
        db.session.commit()
        print(f"\nUsuário '{nome}' criado com sucesso! Já pode fazer login no sistema.")
