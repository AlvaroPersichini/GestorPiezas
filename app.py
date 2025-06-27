from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
#from dotenv import load_dotenv
import os

KEY= os.getenv('KEY')

app = Flask(__name__)
app.secret_key = KEY  # Necesaria para sesiones
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///piezas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



# Modelo Pieza (igual que antes)
class Pieza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50))
    stock = db.Column(db.Integer)
    estado = db.Column(db.String(50))

# Modelo Usuario para login básico
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  

with app.app_context():
    db.create_all()
    # Datos ejemplo piezas
    if not Pieza.query.first():
        db.session.add_all([
            Pieza(codigo="PIE-001", descripcion="Motor de accionamiento 24V", categoria="Electromecánica", stock=12, estado="Disponible"),
            Pieza(codigo="PIE-002", descripcion="Sensor de proximidad", categoria="Sensores", stock=7, estado="Bajo stock"),
            Pieza(codigo="PIE-003", descripcion="Chapa soporte mecanizada", categoria="Mecánica", stock=20, estado="Disponible"),
        ])
    # Datos ejemplo usuario
    if not Usuario.query.first():
        db.session.add(Usuario(username="alvaro.p", email="alvaro@example.com", password="12345678"))
    db.session.commit()

# Ruta Login (GET para mostrar formulario, POST para validar)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        user = Usuario.query.filter_by(username=username, email=email, password=password).first()

        if user:
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login exitoso", "success")
            return redirect(url_for("portal"))
        else:
            flash("Credenciales inválidas", "error")

    return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Verifica si ya existe el usuario
        existente = Usuario.query.filter((Usuario.username == username) | (Usuario.email == email)).first()
        if existente:
            flash("El nombre de usuario o email ya están registrados", "error")
            return redirect(url_for("registro"))

        nuevo_usuario = Usuario(username=username, email=email, password=password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Registro exitoso, ahora puedes iniciar sesión", "success")
        return redirect(url_for("login"))

    return render_template("registro.html")


# Ruta Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for("login"))

# Página principal (portal) protegida, solo usuarios logueados
@app.route("/")
def portal():
    if not session.get("user_id"):
        flash("Por favor logueate primero", "error")
        return redirect(url_for("login"))

    piezas = Pieza.query.all()
    return render_template("portal.html", piezas=piezas, usuario=session.get("username"))

# Las demás rutas (nueva pieza, eliminar) protegidas igual

@app.route("/nueva", methods=["GET", "POST"])
def nueva_pieza():
    if not session.get("user_id"):
        flash("Por favor logueate primero", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        codigo = request.form["codigo"]
        descripcion = request.form["descripcion"]
        categoria = request.form["categoria"]
        stock = int(request.form["stock"])
        estado = request.form["estado"]

        nueva = Pieza(codigo=codigo, descripcion=descripcion, categoria=categoria, stock=stock, estado=estado)
        db.session.add(nueva)
        db.session.commit()
        return redirect(url_for("portal"))
    return render_template("nueva_pieza.html")

@app.route("/eliminar/<int:pieza_id>", methods=["POST"])
def eliminar_pieza(pieza_id):
    if not session.get("user_id"):
        flash("Por favor logueate primero", "error")
        return redirect(url_for("login"))

    pieza = Pieza.query.get_or_404(pieza_id)
    db.session.delete(pieza)
    db.session.commit()
    return redirect(url_for("portal"))




#---------------------------------------------------------------------------------------
# Función doble del if __name__ == '__main__':

# 1. Evita que app.run() se ejecute si el archivo es importado
# Si otro archivo hace import app, entonces:
# __name__ no es '__main__', sino 'app'
# Por lo tanto, el bloque no se ejecuta
# Esto evita que se levante el servidor automáticamente al importar
# Esto permite usar tu archivo como módulo reutilizable

# 2. Hace que app.run() se ejecute solo después de que todo el archivo fue leído y cargado
# Aunque el if esté “antes” en el archivo, Python no lo ejecuta de inmediato
# Python primero lee y ejecuta todo el archivo
# Define funciones, modelos, rutas, etc.
# Recién al final, evalúa y ejecuta el bloque if
# Esto asegura que el servidor Flask arranque solo cuando todo ya está preparado
#---------------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)