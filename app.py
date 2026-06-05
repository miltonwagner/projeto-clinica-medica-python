from flask import Flask, render_template, redirect, request, session
from extensions import db

# =========================
# CONFIGURAÇÃO DA APLICAÇÃO
# =========================

app = Flask(__name__)

# Chave de sessão
app.secret_key = "clinica_vida_plus_2026"

# =========================
# CONFIGURAÇÃO DO BANCO
# =========================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# =========================
# IMPORTAÇÃO DOS MODELOS
# =========================

from models.paciente import Paciente
from models.consulta import Consulta
from models.medico import Medico

# =========================
# IMPORTAÇÃO DOS CONTROLLERS
# =========================

from controllers.paciente_controller import paciente_bp
from controllers.consulta_controller import consulta_bp

app.register_blueprint(paciente_bp)
app.register_blueprint(consulta_bp)

# =========================
# ROTA INICIAL
# =========================

@app.route("/")
def index():
    return render_template("index.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if usuario == "admin" and senha == "123":

            session["logado"] = True

            return redirect("/menu")

        return render_template(
            "login.html",
            erro="Usuário ou senha inválidos."
        )

    return render_template("login.html")


# =========================
# MENU PRINCIPAL
# =========================

@app.route("/menu")
def menu():

    if not session.get("logado"):
        return redirect("/login")

    return render_template("menu.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================
# TRATAMENTO DE ERROS
# =========================

@app.errorhandler(404)
def erro404(error):

    return render_template(
        "errors/404.html"
    ), 404


@app.errorhandler(500)
def erro500(error):

    db.session.rollback()

    return render_template(
        "errors/500.html"
    ), 500


# =========================
# CRIAÇÃO DO BANCO
# =========================

with app.app_context():

    db.create_all()

    # Inserção automática dos médicos
    if Medico.query.count() == 0:

        medico1 = Medico(
            nome="Dr. João Antônio",
            especialidade="Cardiologia"
        )

        medico2 = Medico(
            nome="Dra. Maria Aparecida",
            especialidade="Dermatologia"
        )

        medico3 = Medico(
            nome="Dr. João da Silva",
            especialidade="Clínica Geral"
        )

        db.session.add_all([
            medico1,
            medico2,
            medico3
        ])

        db.session.commit()

        print("✔ Médicos cadastrados com sucesso!")


# =========================
# EXECUÇÃO DA APLICAÇÃO
# =========================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
