"""
models.py
-----------------------------------------------------------------------------
Define as TABELAS do banco de dados usando SQLAlchemy.
-----------------------------------------------------------------------------
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class Usuario(db.Model, UserMixin):
    """
    Representa quem faz LOGIN no sistema. O campo 'tipo' diferencia o nível
    de acesso: 'admin', 'funcionario' ou 'voluntario'.

    Voluntários e funcionários foram unificados nesta única tabela porque
    ambos agora precisam fazer login — antes eram tabelas separadas.
    """
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='funcionario')
    # tipo possíveis: 'admin', 'funcionario', 'voluntario'

    cpf = db.Column(db.String(14))
    telefone = db.Column(db.String(20))
    area_atuacao = db.Column(db.String(100))  # relevante principalmente para voluntários
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    def set_senha(self, senha_texto_puro):
        self.senha_hash = generate_password_hash(senha_texto_puro)

    def verificar_senha(self, senha_texto_puro):
        return check_password_hash(self.senha_hash, senha_texto_puro)

    def __repr__(self):
        return f'<Usuario {self.nome} ({self.tipo})>'


class Animal(db.Model):
    __tablename__ = 'animal'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    especie = db.Column(db.String(30), nullable=False)
    raca = db.Column(db.String(60))
    sexo = db.Column(db.String(10))
    porte = db.Column(db.String(20))
    cor = db.Column(db.String(40))
    idade_aproximada = db.Column(db.String(30))
    descricao = db.Column(db.Text)
    foto_url = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False, default='resgatado')
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    resgates = db.relationship('Resgate', foreign_keys='Resgate.animal_id', backref='animal', lazy=True)
    adocoes = db.relationship('Adocao', backref='animal', lazy=True)
    historico = db.relationship('HistoricoAnimal', backref='animal', lazy=True)

    def __repr__(self):
        return f'<Animal {self.nome} ({self.status})>'


class Resgate(db.Model):
    __tablename__ = 'resgate'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # quem registrou
    responsavel_campo_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)  # quem foi a campo (opcional)

    data_resgate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    local = db.Column(db.String(200))
    condicao_encontrada = db.Column(db.Text)
    observacoes = db.Column(db.Text)

    registrado_por = db.relationship('Usuario', foreign_keys=[usuario_id])
    responsavel_campo = db.relationship('Usuario', foreign_keys=[responsavel_campo_id])

    def __repr__(self):
        return f'<Resgate animal_id={self.animal_id} em {self.data_resgate}>'


class Adotante(db.Model):
    __tablename__ = 'adotante'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cpf = db.Column(db.String(14))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    endereco = db.Column(db.String(255))

    adocoes = db.relationship('Adocao', backref='adotante', lazy=True)

    def __repr__(self):
        return f'<Adotante {self.nome}>'


class Adocao(db.Model):
    __tablename__ = 'adocao'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    adotante_id = db.Column(db.Integer, db.ForeignKey('adotante.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)

    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_conclusao = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pendente')
    observacoes = db.Column(db.Text)

    def __repr__(self):
        return f'<Adocao animal_id={self.animal_id} status={self.status}>'


class HistoricoAnimal(db.Model):
    __tablename__ = 'historico_animal'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    status_anterior = db.Column(db.String(20))
    status_novo = db.Column(db.String(20), nullable=False)
    data_mudanca = db.Column(db.DateTime, default=datetime.utcnow)
    observacao = db.Column(db.Text)

    def __repr__(self):
        return f'<HistoricoAnimal animal_id={self.animal_id} -> {self.status_novo}>'


class Doador(db.Model):
    __tablename__ = 'doador'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cpf_cnpj = db.Column(db.String(20))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))

    doacoes = db.relationship('Doacao', backref='doador', lazy=True)

    def __repr__(self):
        return f'<Doador {self.nome}>'


class Doacao(db.Model):
    __tablename__ = 'doacao'

    id = db.Column(db.Integer, primary_key=True)
    doador_id = db.Column(db.Integer, db.ForeignKey('doador.id'), nullable=True)

    tipo = db.Column(db.String(20), nullable=False)
    valor = db.Column(db.Float, nullable=True)
    item_descricao = db.Column(db.String(255), nullable=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    observacoes = db.Column(db.Text)

    def __repr__(self):
        return f'<Doacao {self.tipo} de {self.doador_id}>'


class ItemEstoque(db.Model):
    """
    Controle de estoque (ração, medicamentos, itens de higiene, etc.).
    """
    __tablename__ = 'item_estoque'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    categoria = db.Column(db.String(50), nullable=False, default='racao')
    # categorias possíveis: 'racao_cao', 'racao_gato', 'medicamento', 'higiene', 'outro'
    quantidade = db.Column(db.Float, nullable=False, default=0)
    unidade = db.Column(db.String(20), nullable=False, default='kg')  # kg, un, L, caixa...
    quantidade_minima = db.Column(db.Float, default=0)  # abaixo disso, mostra alerta
    observacoes = db.Column(db.Text)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ItemEstoque {self.nome}: {self.quantidade}{self.unidade}>'
