from flask import Blueprint, render_template, request, redirect, session
from models.paciente import Paciente
from extensions import db

paciente_bp = Blueprint("paciente", __name__)


# =========================
# 📌 LISTAR + CADASTRAR + BUSCAR
# =========================
@paciente_bp.route("/pacientes", methods=["GET", "POST"])
def pacientes():

    if not session.get("logado"):
        return redirect("/login")

    if request.method == "POST":

        nome = request.form["nome"]
        idade = request.form["idade"]
        telefone = request.form["telefone"]
        email = request.form["email"]

        # Validação simples
        if not nome or not email:
            return "Nome e Email são obrigatórios"

        novo = Paciente(
            nome=nome,
            idade=idade,
            telefone=telefone,
            email=email
        )

        db.session.add(novo)
        db.session.commit()

        return redirect("/pacientes")

    busca = request.args.get("busca")

    if busca:
        pacientes = Paciente.query.filter(
            Paciente.nome.contains(busca)
        ).all()
    else:
        pacientes = Paciente.query.all()

    return render_template(
        "pacientes.html",
        pacientes=pacientes
    )


# =========================
# ✏ EDITAR PACIENTE
# =========================
@paciente_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    if not session.get("logado"):
        return redirect("/login")

    paciente = Paciente.query.get_or_404(id)

    if request.method == "POST":

        paciente.nome = request.form["nome"]
        paciente.idade = request.form["idade"]
        paciente.telefone = request.form["telefone"]
        paciente.email = request.form["email"]

        db.session.commit()

        return redirect("/pacientes")

    return render_template(
        "editar_paciente.html",
        paciente=paciente
    )


# =========================
# 🗑 EXCLUIR PACIENTE
# =========================
@paciente_bp.route("/excluir/<int:id>")
def excluir(id):

    if not session.get("logado"):
        return redirect("/login")

    paciente = Paciente.query.get(id)

    if paciente:
        db.session.delete(paciente)
        db.session.commit()

    return redirect("/pacientes")
