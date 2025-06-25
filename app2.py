from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import mysql.connector

app = Flask(__name__)
app.secret_key = "clave_secreta_segura"

# Conexión a la base de datos MySQL
def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host="localhost",
            user="alvaro",
            password="apersichini86",
            database="GestorPiezas"
        )
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db:
        db.close()

@app.route("/")
def portal():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id, p.nombre AS nombre, p.descripcion, p.codigo_interno, up.cantidad
        FROM piezas p
        JOIN usuario_piezas up ON p.id = up.pieza_id
        WHERE up.usuario_id = %s
    """, (session.get("user_id"),))
    piezas = cursor.fetchall()
    cursor.close()

    return render_template("portal.html", piezas=piezas, usuario=session.get("username"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email=%s AND contrasena=%s",
                       (email, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["nombre"]
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for("portal"))
        else:
            flash("Credenciales inválidas", "error")

    return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
        existente = cursor.fetchone()

        if existente:
            flash("Email ya registrado", "error")
            return redirect(url_for("registro"))

        cursor.execute("INSERT INTO usuarios (nombre, email, contrasena) VALUES (%s, %s, %s)",
                       (nombre, email, password))
        db.commit()
        cursor.close()

        flash("Registro exitoso. Iniciá sesión.", "success")
        return redirect(url_for("login"))

    return render_template("registro.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/nueva", methods=["GET", "POST"])
def nueva_pieza():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    if request.method == "POST":
        nombre = request.form["codigo"]
        descripcion = request.form["descripcion"]
        codigo_interno = request.form["categoria"]
        cantidad = int(request.form["stock"])

        db = get_db()
        cursor = db.cursor()

        # Insertar o ignorar pieza si ya existe
        cursor.execute("SELECT id FROM piezas WHERE codigo_interno = %s", (codigo_interno,))
        pieza = cursor.fetchone()

        if pieza:
            pieza_id = pieza[0]
        else:
            cursor.execute("INSERT INTO piezas (nombre, descripcion, codigo_interno) VALUES (%s, %s, %s)",
                           (nombre, descripcion, codigo_interno))
            db.commit()
            pieza_id = cursor.lastrowid

        # Relacionar con el usuario
        cursor.execute("""
            INSERT INTO usuario_piezas (usuario_id, pieza_id, cantidad)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE cantidad = cantidad + %s
        """, (session.get("user_id"), pieza_id, cantidad, cantidad))
        db.commit()
        cursor.close()

        return redirect(url_for("portal"))

    return render_template("nueva_pieza.html")

@app.route("/eliminar/<int:pieza_id>", methods=["POST"])
def eliminar_pieza(pieza_id):
    if not session.get("user_id"):
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM usuario_piezas WHERE usuario_id = %s AND pieza_id = %s",
                   (session.get("user_id"), pieza_id))
    db.commit()
    cursor.close()

    return redirect(url_for("portal"))

if __name__ == '__main__':
    app.run(debug=True)
