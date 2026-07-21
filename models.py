"""
models.py
-----------------------------------------------------------------------------
Este arquivo define as TABELAS do banco de dados usando SQLAlchemy.

Cada classe abaixo = uma tabela.
Cada atributo da classe = uma coluna dessa tabela.

Isso é chamado de ORM (Object-Relational Mapping): em vez de escrever SQL
puro (CREATE TABLE, INSERT, etc.), a gente escreve classes Python normais,
e o SQLAlchemy converte isso em comandos SQL por trás dos panos.
-----------------------------------------------------------------------------
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 'db' é o objeto que representa a conexão com o banco.
# Ele será usado em app.py também, por isso fica aqui, num lugar central.
db = SQLAlchemy()


class Usuario(db.Model):
    """
    Representa quem faz LOGIN no sistema (administradores/funcionários da ONG).
    Voluntários e adotantes NÃO entram aqui, pois não acessam o sistema.
    """
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)  # nunca salvar senha em texto puro!
    tipo = db.Column(db.String(20), nullable=False, default='admin')  # 'admin' ou 'funcionario'
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Usuario {self.nome}>'


class Animal(db.Model):
    """
    O coração do sistema: cada animal resgatado pela ONG.
    O campo 'status' controla o ciclo de vida do animal dentro do sistema.
    """
    __tablename__ = 'animal'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    especie = db.Column(db.String(30), nullable=False)   # 'cão', 'gato', 'outro'
    raca = db.Column(db.String(60))
    sexo = db.Column(db.String(10))                       # 'macho', 'fêmea'
    porte = db.Column(db.String(20))                       # 'pequeno', 'médio', 'grande'
    cor = db.Column(db.String(40))
    idade_aproximada = db.Column(db.String(30))            # ex: "2 anos", "filhote"
    descricao = db.Column(db.Text)
    foto_url = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False, default='resgatado')
    # status possíveis: 'resgatado', 'em_tratamento', 'disponivel', 'adotado', 'obito'
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos: permitem acessar, a partir de um Animal, todos os
    # registros ligados a ele. Ex: meu_animal.resgates -> lista de resgates
    resgates = db.relationship('Resgate', backref='animal', lazy=True)
    adocoes = db.relationship('Adocao', backref='animal', lazy=True)
    historico = db.relationship('HistoricoAnimal', backref='animal', lazy=True)

    def __repr__(self):
        return f'<Animal {self.nome} ({self.status})>'


class Voluntario(db.Model):
    """
    Cadastro simples de voluntários (sem login no sistema).
    """
    __tablename__ = 'voluntario'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cpf = db.Column(db.String(14))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    area_atuacao = db.Column(db.String(100))  # ex: "resgate", "transporte", "divulgação"
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Voluntario {self.nome}>'


class Resgate(db.Model):
    """
    Histórico de como e quando cada animal foi resgatado.
    """
    __tablename__ = 'resgate'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # quem registrou
    voluntario_id = db.Column(db.Integer, db.ForeignKey('voluntario.id'), nullable=True)  # quem foi a campo (opcional)

    data_resgate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    local = db.Column(db.String(200))
    condicao_encontrada = db.Column(db.Text)  # descrição do estado do animal ao ser resgatado
    observacoes = db.Column(db.Text)

    def __repr__(self):
        return f'<Resgate animal_id={self.animal_id} em {self.data_resgate}>'


class Adotante(db.Model):
    """
    Pessoa interessada em adotar. Não precisa de login.
    """
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
    """
    Liga um Animal a um Adotante. Um animal pode ter várias TENTATIVAS
    de adoção ao longo do tempo (por isso é uma tabela separada, e não
    só um campo dentro de Animal).
    """
    __tablename__ = 'adocao'

    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    adotante_id = db.Column(db.Integer, db.ForeignKey('adotante.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)  # quem aprovou/avaliou

    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_conclusao = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pendente')
    # status possíveis: 'pendente', 'em_avaliacao', 'aprovada', 'recusada', 'concluida'
    observacoes = db.Column(db.Text)

    def __repr__(self):
        return f'<Adocao animal_id={self.animal_id} status={self.status}>'


class HistoricoAnimal(db.Model):
    """
    Registra toda mudança de status de um animal, criando uma linha do
    tempo. Isso é ótimo para o dashboard (ex: 'quantos animais viraram
    disponíveis este mês') e para mostrar rastreabilidade no TCC.
    """
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
    """
    Pessoa ou empresa que faz doações. Pode ser anônimo (nome genérico).
    """
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
    """
    Registro de uma doação, financeira ou material.
    """
    __tablename__ = 'doacao'

    id = db.Column(db.Integer, primary_key=True)
    doador_id = db.Column(db.Integer, db.ForeignKey('doador.id'), nullable=True)  # nullable p/ doação anônima

    tipo = db.Column(db.String(20), nullable=False)  # 'financeira' ou 'material'
    valor = db.Column(db.Float, nullable=True)         # usado se tipo == 'financeira'
    item_descricao = db.Column(db.String(255), nullable=True)  # usado se tipo == 'material'
    data = db.Column(db.DateTime, default=datetime.utcnow)
    observacoes = db.Column(db.Text)

    def __repr__(self):
        return f'<Doacao {self.tipo} de {self.doador_id}>'
