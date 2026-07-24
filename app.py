"""
app.py
-----------------------------------------------------------------------------
Ponto de entrada da aplicação Flask.
-----------------------------------------------------------------------------
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from models import db, Animal, HistoricoAnimal

app = Flask(__name__)
app.secret_key = 'troque-esta-chave-antes-de-colocar-em-producao'  # necessário para usar flash()

# Configuração da pasta onde as fotos enviadas serão salvas
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # cria a pasta se ainda não existir
EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'webp'}


def extensao_permitida(nome_arquivo):
    return '.' in nome_arquivo and nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS


def salvar_foto(arquivo):
    """Salva a foto enviada (se houver) e devolve o caminho relativo para guardar no banco.
    Se nenhum arquivo válido for enviado, devolve None."""
    if not arquivo or arquivo.filename == '':
        return None
    if not extensao_permitida(arquivo.filename):
        flash('Formato de imagem não suportado. Use PNG, JPG ou WEBP.', 'erro')
        return None

    nome_seguro = secure_filename(arquivo.filename)
    from datetime import datetime
    nome_final = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{nome_seguro}"

    caminho_completo = os.path.join(app.config['UPLOAD_FOLDER'], nome_final)
    arquivo.save(caminho_completo)

    return f'uploads/{nome_final}'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ong.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    print("Banco de dados criado/verificado com sucesso: ong.db")


@app.route('/')
def index():
    return redirect(url_for('listar_animais'))


@app.route('/animais')
def listar_animais():
    animais = Animal.query.order_by(Animal.data_cadastro.desc()).all()
    return render_template('animais/lista.html', animais=animais)


@app.route('/animais/novo', methods=['GET', 'POST'])
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
def detalhe_animal(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    return render_template('animais/detalhe.html', animal=animal)


@app.route('/animais/<int:animal_id>/editar', methods=['GET', 'POST'])
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


if __name__ == '__main__':
    app.run(debug=True)
