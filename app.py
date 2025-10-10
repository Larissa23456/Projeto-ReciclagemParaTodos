from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(20)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # rota que será usada para login
login_manager.login_message = "Por favor, faça login para acessar esta página."

# Cria a tabela usuário
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    cep = db.Column(db.String(8), nullable=False)
    numero = db.Column(db.Integer, nullable=False) # VERIFICAR SE PRECISAM SER NULAS
    email = db.Column(db.String(150), nullable=False)
    senha = db.Column(db.String(150), nullable=False)
    pontuacao = db.Column(db.Integer, default=0)

class User_empresa(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    numero = db.Column(db.Integer, nullable=False) # VERIFICAR SE PRECISAM SER NULAS
    email = db.Column(db.String(150), nullable=False)
    cnpj = db.Column(db.String(8), nullable=False)
    senha = db.Column(db.String(150), nullable=False)
    pontuacao = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if user:
        return user
    return User_empresa.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
@login_required
def pagina_inicial():
    # Descobre a maior pontuação
    maior_pontuacao = db.session.query(db.func.max(User.pontuacao)).scalar()

    # Seleciona todos os usuários que têm essa pontuação
    top_usuarios = User.query.filter_by(pontuacao=maior_pontuacao).all()

    return render_template('pagina_inicial.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    return render_template('cadastro.html')

@app.route('/cadastro_moradores', methods=['GET', 'POST'])
def cadastro_moradores():
    if request.method == 'POST':
        nome = request.form['nome']
        cep = request.form['cep']
        numero = request.form['numero']
        email = request.form['email']
        senha = request.form['senha']
        confirmarSenha = request.form['confirmarSenha']

        # Verifica se o checkbox "remember" foi marcado
        remember = 'remember' in request.form 

        if senha != confirmarSenha:
            flash('As senhas não coincidem. Tente novamente.', 'danger')
            return redirect(url_for('cadastro_moradores'))

        new_user = User(
            nome=nome,
            cep=cep,
            numero=numero,
            email=email,
            senha=generate_password_hash(senha, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()

        # Faz login já com o parâmetro remember
        login_user(new_user, remember=remember)

        flash(f"Usuário {nome} cadastrado com sucesso!", "success")
        return redirect(url_for('pagina_inicial'))
    
    return render_template('cadastro_moradores.html')

@app.route('/cadastro_empresa', methods=['GET', 'POST'])
def cadastro_empresa():
    if request.method == 'POST':
        nome = request.form['nome']
        numero = request.form['numero']
        email = request.form['email']
        cnpj = request.form['cnpj']
        senha = request.form['senha']
        confirmarSenha = request.form['confirmarSenha']

        # Captura o checkbox "remember" do formulário
        remember = 'remember' in request.form

        if senha != confirmarSenha:
            flash('As senhas não coincidem. Tente novamente.', 'danger')
            return redirect(url_for('cadastro_empresa'))  # Corrigido para redirecionar para a rota correta

        new_user = User_empresa(
            nome=nome,
            numero=numero,
            email=email,
            cnpj=cnpj,
            senha=generate_password_hash(senha, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()

        # Faz login já com o parâmetro remember
        login_user(new_user, remember=remember)

        flash(f"Empresa {nome} cadastrada com sucesso!", "success")
        return redirect(url_for('pagina_inicial'))
    
    return render_template('cadastro_empresa.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        tipo_usuario = request.form.get('tipo_usuario')
        remember = 'remember' in request.form

        if tipo_usuario == 'morador':
            user = User.query.filter_by(email=email).first()
        elif tipo_usuario == 'empresa':
            user = User_empresa.query.filter_by(email=email).first()
        else:
            user = None

        if user and check_password_hash(user.senha, senha):
            login_user(user, remember=remember)
            flash(f"Login feito com sucesso como {tipo_usuario}.", "success")
            return redirect(url_for('pagina_inicial'))
        else:
            flash("E-mail ou senha inválidos. Tente novamente.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')


if __name__ == '__main__':
    if not os.path.exists('database.db'):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
