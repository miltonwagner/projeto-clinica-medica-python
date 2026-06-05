from flask import Blueprint, render_template, request, redirect, session
from extensions import db

from models.consulta import Consulta
from models.paciente import Paciente
from models.medico import Medico

from utils.email_service import enviar_email

consulta_bp = Blueprint("consulta", __name__)


# ==================================
# LISTAR CONSULTAS
# ==================================
@consulta_bp.route("/consultas")
def consultas():

    if not session.get("logado"):
        return redirect("/login")

    status = request.args.get("status")

    if status:
        lista = Consulta.query.filter_by(status=status).all()
    else:
        lista = Consulta.query.all()

    return render_template(
        "consultas.html",
        lista=lista
    )


# ==================================
# AGENDAR CONSULTA
# ==================================
@consulta_bp.route("/agendar", methods=["GET", "POST"])
def agendar():

    if not session.get("logado"):
        return redirect("/login")

    pacientes = Paciente.query.all()
    medicos = Medico.query.all()

    if request.method == "POST":

        paciente_id = request.form["paciente_id"]
        medico_id = request.form["medico_id"]
        data = request.form["data"]
        hora = request.form["hora"]

        # Verifica conflito de horário
        conflito = Consulta.query.filter_by(
            medico_id=medico_id,
            data=data,
            hora=hora,
            status="Agendada"
        ).first()

        if conflito:
            return "❌ Este horário já está ocupado."

        nova_consulta = Consulta(
            paciente_id=paciente_id,
            medico_id=medico_id,
            data=data,
            hora=hora,
            status="Agendada"
        )

        db.session.add(nova_consulta)
        db.session.commit()

        paciente = Paciente.query.get(paciente_id)
        medico = Medico.query.get(medico_id)

        try:
            enviar_email(
                paciente.email,
                paciente.nome,
                data,
                hora,
                medico.nome
            )
        except:
            pass

        return redirect("/consultas")

    return render_template(
        "agendar.html",
        pacientes=pacientes,
        medicos=medicos
    )


# ==================================
# CANCELAR CONSULTA
# ==================================
@consulta_bp.route("/cancelar/<int:id>")
def cancelar(id):

    if not session.get("logado"):
        return redirect("/login")

    consulta = Consulta.query.get_or_404(id)

    consulta.status = "Cancelada"

    db.session.commit()

    return redirect("/consultas")


# ==================================
# REAGENDAR CONSULTA
# ==================================
@consulta_bp.route("/reagendar/<int:id>", methods=["GET", "POST"])
def reagendar(id):

    if not session.get("logado"):
        return redirect("/login")

    consulta = Consulta.query.get_or_404(id)

    if request.method == "POST":

        nova_data = request.form["data"]
        nova_hora = request.form["hora"]

        conflito = Consulta.query.filter(
            Consulta.medico_id == consulta.medico_id,
            Consulta.data == nova_data,
            Consulta.hora == nova_hora,
            Consulta.status == "Agendada",
            Consulta.id != consulta.id
        ).first()

        if conflito:
            return "❌ Este horário já está ocupado."

        consulta.data = nova_data
        consulta.hora = nova_hora

        db.session.commit()

        return redirect("/consultas")

    return render_template(
        "reagendar.html",
        consulta=consulta
    )
