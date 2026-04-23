from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "seguro_2026"


def db():
    return sqlite3.connect("usuarios.db")


def init_db():
    con = db()
    c = con.cursor()

    # TABLA USUARIOS
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        usuario TEXT PRIMARY KEY,
        password TEXT,
        rol TEXT
    )
    """)

    # 🔥 TABLA ESTUDIANTES COMPLETA
    c.execute("""
    CREATE TABLE IF NOT EXISTS estudiantes (
        documento TEXT PRIMARY KEY,
        nombre TEXT,
        correo TEXT,
        programa TEXT,
        estado TEXT,
        resolucion TEXT
    )
    """)

    # ADMIN OCULTO
    c.execute("SELECT * FROM usuarios WHERE usuario='root2026'")
    if not c.fetchone():
        c.execute("INSERT INTO usuarios VALUES (?,?,?)", (
            "root2026",
            generate_password_hash("Admin#2026"),
            "admin"
        ))

    con.commit()
    con.close()


init_db()

# ---------------- LOGIN ----------------

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/ingresar", methods=["POST"])
def ingresar():
    user = request.form.get("usuario")
    pwd = request.form.get("password")

    con = db()
    c = con.cursor()
    c.execute("SELECT * FROM usuarios WHERE usuario=?", (user,))
    data = c.fetchone()
    con.close()

    if data and check_password_hash(data[1], pwd):
        session["usuario"] = data[0]
        session["rol"] = data[2]

        if data[2] == "admin":
            return redirect("/panel-interno-icesi-2026")
        else:
            return redirect("/panel")

    return "Datos incorrectos"


# 🔐 ADMIN OCULTO
@app.route("/panel-interno-icesi-2026")
def admin():
    if session.get("rol") != "admin":
        return redirect("/")

    con = db()
    c = con.cursor()
    c.execute("SELECT * FROM estudiantes")
    estudiantes = c.fetchall()
    con.close()

    return render_template("admin.html", estudiantes=estudiantes)


# CREAR ESTUDIANTE
@app.route("/crear", methods=["POST"])
def crear():
    if session.get("rol") != "admin":
        return redirect("/")

    documento = request.form.get("documento")
    nombre = request.form.get("nombre")
    correo = request.form.get("correo")
    programa = request.form.get("programa")
    estado = request.form.get("estado")
    resolucion = request.form.get("resolucion")

    con = db()
    c = con.cursor()

    try:
        c.execute("INSERT INTO usuarios VALUES (?,?,?)",
                  (documento, generate_password_hash(documento), "estudiante"))

        c.execute("INSERT INTO estudiantes VALUES (?,?,?,?,?,?)",
                  (documento, nombre, correo, programa, estado, resolucion))

        con.commit()
    except:
        con.close()
        return "El estudiante ya existe"

    con.close()
    return redirect("/panel-interno-icesi-2026")


# PANEL ESTUDIANTE
@app.route("/panel")
def panel():
    if session.get("rol") != "estudiante":
        return redirect("/")

    user = session["usuario"]

    con = db()
    c = con.cursor()
    c.execute("SELECT * FROM estudiantes WHERE documento=?", (user,))
    row = c.fetchone()
    con.close()

    estudiante = {
        "documento": row[0],
        "nombre": row[1],
        "correo": row[2],
        "programa": row[3],
        "estado": row[4],
        "resolucion": row[5]
    }

    return render_template("panel.html", estudiante=estudiante)


# SALIR
@app.route("/salir")
def salir():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)