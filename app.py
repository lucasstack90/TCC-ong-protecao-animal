"""
app.py
-----------------------------------------------------------------------------
Ponto de entrada da aplicação Flask.
-----------------------------------------------------------------------------
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from models import db, Animal, HistoricoAnimal, Adotante, Doador, Usuario, ItemEstoque

app = Flask(__name__)
app.secret_key = 'troque-esta-chave-antes-de-colocar-em-producao'

# ----------------------------------------------------------------------
# CONFIGURAÇÃO DO BANCO DE DADOS (MySQL via XAMPP)
# ----------------------------------------------------------------------
# Formato: mysql+pymysql://usuario:senha@host/nome_do_banco
# No XAMPP, por padrão o usuário é 'root' e a senha é vazia.
# IMPORTANTE: o banco 'ong_sistema' precisa já existir no phpMyAdmin
# antes de rodar esse arquivo (o SQLAlchemy cria as TABELAS, mas não
# cria o banco de dados em si).
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ong_user:ong_senha123@localhost/ong_sistema'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'webp'}

db.init_app(app)

# ----------------------------------------------------------------------
# CONFIGURAÇÃO DO LOGIN (Flask-Login)
# ----------------------------------------------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Faça login para acessar o sistema.'
login_manager.login_message_category = 'erro'


@login_manager.user_loader
def carregar_usuario(usuario_id):
    return Usuario.query.get(int(usuario_id))


with app.app_context():
    db.create_all()
    print("Tabelas criadas/verificadas com sucesso no MySQL (banco: ong_sistema)")


def extensao_permitida(nome_arquivo):
    return '.' in nome_arquivo and nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS


def salvar_foto(arquivo):
    if not arquivo or arquivo.filename == '':
        return None
    if not extensao_permitida(arquivo.filename):
        flash('Formato de imagem não suportado. Use PNG, JPG ou WEBP.', 'erro')
        return None
    nome_seguro = secure_filename(arquivo.filename)
    nome_final = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{nome_seguro}"
    arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_final))
    return f'uploads/{nome_final}'


def apenas_admin():
    """Verifica se o usuário logado é admin. Usado para proteger áreas sensíveis
    (como criar novos logins de funcionário/voluntário)."""
    return current_user.is_authenticated and current_user.tipo == 'admin'


# ----------------------------------------------------------------------
# ROTAS DE LOGIN / LOGOUT
# ----------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('listar_animais'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and not usuario.ativo:
            flash('Este usuário está inativo. Fale com um administrador.', 'erro')
        elif usuario and usuario.verificar_senha(senha):
            login_user(usuario)
            flash(f'Bem-vindo(a), {usuario.nome}!', 'sucesso')
            proxima_pagina = request.args.get('next')
            return redirect(proxima_pagina or url_for('listar_animais'))
        else:
            flash('Email ou senha incorretos.', 'erro')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'sucesso')
    return redirect(url_for('login'))


# ----------------------------------------------------------------------
# ROTAS DE ANIMAIS
# ----------------------------------------------------------------------

@app.route('/')
@login_required
def index():
    return redirect(url_for('listar_animais'))


@app.route('/animais')
@login_required
def listar_animais():
    animais = Animal.query.order_by(Animal.data_cadastro.desc()).all()
    return render_template('animais/lista.html', animais=animais)


@app.route('/animais/novo', methods=['GET', 'POST'])
@login_required
def novo_animal():
    if request.method == 'POST':
        foto_path = salvar_foto(request.files.get('foto'))
        animal = Animal(
            nome=request.form['nome'],
            especie=request.form['especie'],
            raca=request.form.get('raca'),
            sexo=request.form.get('sexo'),
            porte=request.form.get('porte'),
            cor=request.form.get('cor'),
            idade_aproximada=request.form.get('idade_aproximada'),
            descricao=request.form.get('descricao'),
            status=request.form.get('status', 'resgatado'),
            foto_url=foto_path,
        )
        db.session.add(animal)
        db.session.flush()

        db.session.add(HistoricoAnimal(
            animal_id=animal.id,
            status_anterior=None,
            status_novo=animal.status,
            observacao='Cadastro inicial do animal',
        ))
        db.session.commit()
        flash('Animal cadastrado com sucesso!', 'sucesso')
        return redirect(url_for('listar_animais'))

    return render_template('animais/form.html', animal=None)


@app.route('/animais/<int:animal_id>')
@login_required
def detalhe_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    return render_template('animais/detalhe.html', animal=animal)


@app.route('/animais/<int:animal_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)

    if request.method == 'POST':
        status_anterior = animal.status
        status_novo = request.form.get('status', animal.status)

        animal.nome = request.form['nome']
        animal.especie = request.form['especie']
        animal.raca = request.form.get('raca')
        animal.sexo = request.form.get('sexo')
        animal.porte = request.form.get('porte')
        animal.cor = request.form.get('cor')
        animal.idade_aproximada = request.form.get('idade_aproximada')
        animal.descricao = request.form.get('descricao')
        animal.status = status_novo

        novo_foto_path = salvar_foto(request.files.get('foto'))
        if novo_foto_path:
            animal.foto_url = novo_foto_path

        if status_anterior != status_novo:
            db.session.add(HistoricoAnimal(
                animal_id=animal.id,
                status_anterior=status_anterior,
                status_novo=status_novo,
            ))

        db.session.commit()
        flash('Animal atualizado com sucesso!', 'sucesso')
        return redirect(url_for('detalhe_animal', animal_id=animal.id))

    return render_template('animais/form.html', animal=animal)


# ----------------------------------------------------------------------
# ROTAS DE USUÁRIOS (funcionários e voluntários — ambos fazem login)
# ----------------------------------------------------------------------
# URL continua '/voluntarios' por familiaridade, mas agora administra
# registros de Usuario com tipo 'funcionario' ou 'voluntario'.

@app.route('/voluntarios')
@login_required
def listar_voluntarios():
    pessoas = Usuario.query.filter(
        Usuario.tipo.in_(['funcionario', 'voluntario'])
    ).order_by(Usuario.ativo.desc(), Usuario.data_cadastro.desc()).all()
    return render_template('voluntarios/lista.html', pessoas=pessoas)


@app.route('/voluntarios/novo', methods=['GET', 'POST'])
@login_required
def novo_voluntario():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()

        if Usuario.query.filter_by(email=email).first():
            flash('Já existe um usuário cadastrado com esse email.', 'erro')
            return render_template('voluntarios/form.html', pessoa=None)

        pessoa = Usuario(
            nome=request.form['nome'],
            email=email,
            tipo=request.form.get('tipo', 'voluntario'),
            cpf=request.form.get('cpf'),
            telefone=request.form.get('telefone'),
            area_atuacao=request.form.get('area_atuacao'),
        )
        pessoa.set_senha(request.form.get('senha') or '123456')  # senha provisória se não informada
        db.session.add(pessoa)
        db.session.commit()
        flash(f'{pessoa.nome} cadastrado(a) com sucesso! Peça para trocar a senha no primeiro acesso.', 'sucesso')
        return redirect(url_for('listar_voluntarios'))

    return render_template('voluntarios/form.html', pessoa=None)


@app.route('/voluntarios/<int:pessoa_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_voluntario(pessoa_id):
    pessoa = Usuario.query.get_or_404(pessoa_id)

    if request.method == 'POST':
        pessoa.nome = request.form['nome']
        pessoa.tipo = request.form.get('tipo', pessoa.tipo)
        pessoa.cpf = request.form.get('cpf')
        pessoa.telefone = request.form.get('telefone')
        pessoa.area_atuacao = request.form.get('area_atuacao')

        nova_senha = request.form.get('senha')
        if nova_senha:  # só troca a senha se algo foi digitado
            pessoa.set_senha(nova_senha)

        db.session.commit()
        flash('Cadastro atualizado com sucesso!', 'sucesso')
        return redirect(url_for('listar_voluntarios'))

    return render_template('voluntarios/form.html', pessoa=pessoa)


@app.route('/voluntarios/<int:pessoa_id>/alternar-status', methods=['POST'])
@login_required
def alternar_status_voluntario(pessoa_id):
    pessoa = Usuario.query.get_or_404(pessoa_id)
    pessoa.ativo = not pessoa.ativo
    db.session.commit()
    mensagem = f'{pessoa.nome} reativado(a)!' if pessoa.ativo else f'{pessoa.nome} marcado(a) como inativo(a).'
    flash(mensagem, 'sucesso')
    return redirect(url_for('listar_voluntarios'))


# ----------------------------------------------------------------------
# ROTAS DE ADOTANTES
# ----------------------------------------------------------------------

@app.route('/adotantes')
@login_required
def listar_adotantes():
    adotantes = Adotante.query.order_by(Adotante.nome).all()
    return render_template('adotantes/lista.html', adotantes=adotantes)


@app.route('/adotantes/novo', methods=['GET', 'POST'])
@login_required
def novo_adotante():
    if request.method == 'POST':
        adotante = Adotante(
            nome=request.form['nome'],
            cpf=request.form.get('cpf'),
            telefone=request.form.get('telefone'),
            email=request.form.get('email'),
            endereco=request.form.get('endereco'),
        )
        db.session.add(adotante)
        db.session.commit()
        flash('Adotante cadastrado com sucesso!', 'sucesso')
        return redirect(url_for('listar_adotantes'))

    return render_template('adotantes/form.html', adotante=None)


@app.route('/adotantes/<int:adotante_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_adotante(adotante_id):
    adotante = Adotante.query.get_or_404(adotante_id)

    if request.method == 'POST':
        adotante.nome = request.form['nome']
        adotante.cpf = request.form.get('cpf')
        adotante.telefone = request.form.get('telefone')
        adotante.email = request.form.get('email')
        adotante.endereco = request.form.get('endereco')
        db.session.commit()
        flash('Adotante atualizado com sucesso!', 'sucesso')
        return redirect(url_for('listar_adotantes'))

    return render_template('adotantes/form.html', adotante=adotante)


# ----------------------------------------------------------------------
# ROTAS DE DOADORES
# ----------------------------------------------------------------------

@app.route('/doadores')
@login_required
def listar_doadores():
    doadores = Doador.query.order_by(Doador.nome).all()
    return render_template('doadores/lista.html', doadores=doadores)


@app.route('/doadores/novo', methods=['GET', 'POST'])
@login_required
def novo_doador():
    if request.method == 'POST':
        doador = Doador(
            nome=request.form['nome'],
            cpf_cnpj=request.form.get('cpf_cnpj'),
            telefone=request.form.get('telefone'),
            email=request.form.get('email'),
        )
        db.session.add(doador)
        db.session.commit()
        flash('Doador cadastrado com sucesso!', 'sucesso')
        return redirect(url_for('listar_doadores'))

    return render_template('doadores/form.html', doador=None)


@app.route('/doadores/<int:doador_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_doador(doador_id):
    doador = Doador.query.get_or_404(doador_id)

    if request.method == 'POST':
        doador.nome = request.form['nome']
        doador.cpf_cnpj = request.form.get('cpf_cnpj')
        doador.telefone = request.form.get('telefone')
        doador.email = request.form.get('email')
        db.session.commit()
        flash('Doador atualizado com sucesso!', 'sucesso')
        return redirect(url_for('listar_doadores'))

    return render_template('doadores/form.html', doador=doador)


# ----------------------------------------------------------------------
# ROTAS DE ESTOQUE
# ----------------------------------------------------------------------

@app.route('/estoque')
@login_required
def listar_estoque():
    itens = ItemEstoque.query.order_by(ItemEstoque.nome).all()
    return render_template('estoque/lista.html', itens=itens)


@app.route('/estoque/novo', methods=['GET', 'POST'])
@login_required
def novo_item_estoque():
    if request.method == 'POST':
        item = ItemEstoque(
            nome=request.form['nome'],
            categoria=request.form.get('categoria', 'outro'),
            quantidade=float(request.form.get('quantidade') or 0),
            unidade=request.form.get('unidade', 'kg'),
            quantidade_minima=float(request.form.get('quantidade_minima') or 0),
            observacoes=request.form.get('observacoes'),
        )
        db.session.add(item)
        db.session.commit()
        flash('Item de estoque cadastrado com sucesso!', 'sucesso')
        return redirect(url_for('listar_estoque'))

    return render_template('estoque/form.html', item=None)


@app.route('/estoque/<int:item_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_item_estoque(item_id):
    item = ItemEstoque.query.get_or_404(item_id)

    if request.method == 'POST':
        item.nome = request.form['nome']
        item.categoria = request.form.get('categoria', item.categoria)
        item.quantidade = float(request.form.get('quantidade') or 0)
        item.unidade = request.form.get('unidade', item.unidade)
        item.quantidade_minima = float(request.form.get('quantidade_minima') or 0)
        item.observacoes = request.form.get('observacoes')
        db.session.commit()
        flash('Item de estoque atualizado com sucesso!', 'sucesso')
        return redirect(url_for('listar_estoque'))

    return render_template('estoque/form.html', item=item)


if __name__ == '__main__':
    app.run(debug=True)
