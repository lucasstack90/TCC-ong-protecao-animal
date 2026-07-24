"""
app.py
-----------------------------------------------------------------------------
Ponto de entrada da aplicação Flask.

Por enquanto, ele só:
  1. Cria a aplicação Flask
  2. Configura o banco de dados (SQLite, um arquivo local chamado ong.db)
  3. Cria as tabelas a partir dos models definidos em models.py

Nas próximas etapas vamos adicionar as ROTAS (páginas/URLs) do sistema.
-----------------------------------------------------------------------------
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Animal, HistoricoAnimal, Voluntario

app = Flask(__name__)
app.secret_key = 'troque-esta-chave-antes-de-colocar-em-producao'  # necessário para usar flash()

# Configuração do banco: SQLite salva tudo num arquivo local, sem precisar
# instalar servidor de banco de dados. Ótimo para desenvolvimento.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ong.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Conecta o SQLAlchemy (definido em models.py) a esta aplicação Flask
db.init_app(app)

# Cria as tabelas no banco (só cria se ainda não existirem)
with app.app_context():
    db.create_all()
    print("Banco de dados criado/verificado com sucesso: ong.db")


# ----------------------------------------------------------------------
# ROTAS DE ANIMAIS
# ----------------------------------------------------------------------
# Cada 'rota' é uma URL que o navegador pode acessar. A função abaixo dela
# roda quando alguém visita essa URL.

@app.route('/')
def index():
    # Por enquanto, a página inicial redireciona direto para a lista de animais
    return redirect(url_for('listar_animais'))


@app.route('/animais')
def listar_animais():
    # Busca todos os animais no banco, ordenados pelos mais recentes primeiro
    animais = Animal.query.order_by(Animal.data_cadastro.desc()).all()
    return render_template('animais/lista.html', animais=animais)


@app.route('/animais/novo', methods=['GET', 'POST'])
def novo_animal():
    if request.method == 'POST':
        # request.form contém os dados enviados pelo formulário
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
        )
        db.session.add(animal)
        db.session.flush()  # garante que animal.id já existe antes de criar o histórico

        # Registra a criação no histórico também
        db.session.add(HistoricoAnimal(
            animal_id=animal.id,
            status_anterior=None,
            status_novo=animal.status,
            observacao='Cadastro inicial do animal',
        ))

        db.session.commit()
        flash('Animal cadastrado com sucesso!', 'sucesso')
        return redirect(url_for('listar_animais'))

    # Se for GET, só mostra o formulário vazio
    return render_template('animais/form.html', animal=None)


@app.route('/animais/<int:animal_id>')
def detalhe_animal(animal_id):
    # get_or_404: busca pelo id, ou mostra página de erro 404 se não existir
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

        # Se o status mudou, registra no histórico automaticamente
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
# ROTAS DE VOLUNTÁRIOS
# ----------------------------------------------------------------------
# Segue exatamente o mesmo padrão das rotas de Animal acima.

@app.route('/voluntarios')
def listar_voluntarios():
    # Mostra primeiro os voluntários ativos, depois os inativos, mais recentes primeiro
    voluntarios = Voluntario.query.order_by(
        Voluntario.ativo.desc(), Voluntario.data_cadastro.desc()
    ).all()
    return render_template('voluntarios/lista.html', voluntarios=voluntarios)


@app.route('/voluntarios/novo', methods=['GET', 'POST'])
def novo_voluntario():
    if request.method == 'POST':
        voluntario = Voluntario(
            nome=request.form['nome'],
            cpf=request.form.get('cpf'),
            telefone=request.form.get('telefone'),
            email=request.form.get('email'),
            area_atuacao=request.form.get('area_atuacao'),
        )
        db.session.add(voluntario)
        db.session.commit()
        flash('Voluntário cadastrado com sucesso!', 'sucesso')
        return redirect(url_for('listar_voluntarios'))

    # Se for GET, só mostra o formulário vazio
    return render_template('voluntarios/form.html', voluntario=None)


@app.route('/voluntarios/<int:voluntario_id>/editar', methods=['GET', 'POST'])
def editar_voluntario(voluntario_id):
    voluntario = Voluntario.query.get_or_404(voluntario_id)

    if request.method == 'POST':
        voluntario.nome = request.form['nome']
        voluntario.cpf = request.form.get('cpf')
        voluntario.telefone = request.form.get('telefone')
        voluntario.email = request.form.get('email')
        voluntario.area_atuacao = request.form.get('area_atuacao')

        db.session.commit()
        flash('Voluntário atualizado com sucesso!', 'sucesso')
        return redirect(url_for('listar_voluntarios'))

    return render_template('voluntarios/form.html', voluntario=voluntario)


@app.route('/voluntarios/<int:voluntario_id>/alternar-status', methods=['POST'])
def alternar_status_voluntario(voluntario_id):
    # Em vez de apagar o voluntário do banco (o que perderia o histórico),
    # a gente só liga/desliga o campo 'ativo'. Isso é uma prática comum
    # chamada de "soft delete".
    voluntario = Voluntario.query.get_or_404(voluntario_id)
    voluntario.ativo = not voluntario.ativo
    db.session.commit()

    mensagem = 'Voluntário reativado!' if voluntario.ativo else 'Voluntário marcado como inativo.'
    flash(mensagem, 'sucesso')
    return redirect(url_for('listar_voluntarios'))


if __name__ == '__main__':
    app.run(debug=True)
