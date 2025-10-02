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


# Cria a tabela usuário
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
@login_required
def pagina_inicial():
    return render_template('pagina_inicial.html')


# CADASTRO DA EMPRESA
@app.route('/cadastrar_empresa', methods=['GET', 'POST'])
def cadastro_empresa():
    return render_template('cadastro_empresa.html')


# CADASTRO DO USUARIO
@app.route('/cadastrar_usuario', methods=['GET', 'POST'])
def cadastro_usuario():
    return render_template('cadastro_usuario.html')


# CADASTRO DOS MORADORES
@app.route('/cadastrar_moradores', methods=['GET', 'POST'])
def cadastro_moradores():
    return render_template('cadastro_morador.html')


# PAGINA DE LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


if __name__ == '__main__':
    if not os.path.exists('database.db'):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
