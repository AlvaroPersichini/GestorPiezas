from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import mysql.connector
from dotenv import load_dotenv
import os


# "request":
# request es un objeto global de Flask que representa la solicitud HTTP que hizo el navegador
# Flask lo mantiene disponible durante la vida de una petición, usando algo llamado "contexto de aplicación"
# ----------------------------------------------

# "cursor" y "mysql.connector":
# es un objeto que se obtiene a partir de la conexión a la base de datos.
# Permite ejecutar consultas SQL (SELECT, INSERT, etc.) y acceder a los resultados
# "dictionary=True" hace que cada fila venga como un diccionario ({'id': 1, 'nombre': 'Juan'}), en lugar de tupla.
# Nota: el cursor lo devuelve el conector MySQL, no Flask. Seguramente estás usando mysql.connector
# ----------------------------------------------

# "os":
# "os" es un módulo estándar de Python 
# para interactuar con el sistema operativo.
# En este proyecto se usa principalmente para leer variables de entorno,
# como 'SECRET_KEY', sin tener que escribir datos sensibles directamente en el código.
# app.secret_key = os.environ.get("SECRET_KEY")
# ----------------------------------------------

# "g":
# Es un objeto especial de Flask
# Es una especie de bolsillo global temporal que vive durante una sola petición HTTP.
# Sirve para guardar datos que queremos reutilizar a lo largo de esa petición, como una conexión a la base de datos.
# Cuando la petición termina, g se borra.
# g dura solo durante una sola petición HTTP (una sola interacción entre navegador y servidor).
# Por eso, g.db se reutiliza solo dentro de la misma petición, por ejemplo:
# Si en tu código tienes varias funciones o partes que necesitan acceder a la base de datos,
# todas usarán la misma conexión guardada en g.db.
# Así no se abre una conexión nueva cada vez que necesitás consultar algo dentro de esa misma petición.
# ----------------------------------------------


# "session":
# 'session' es un objeto especial de Flask que permite almacenar datos 
# específicos de un usuario entre diferentes peticiones (requests).
# Utiliza cookies firmadas para mantener la información del lado del cliente,
# asegurando integridad mediante la SECRET_KEY de la app.
# Se usa comúnmente para:
# - Guardar el estado de login (por ejemplo: session['usuario_id'] = 5)
# - Recordar preferencias del usuario temporalmente
# Los datos se eliminan al cerrar el navegador o con session.clear(), 
# a menos que se configure un tiempo de expiración.
# Ejemplo de uso:
#   session['usuario'] = 'alvaro'
#   usuario = session.get('usuario')
# ----------------------------------------------





# ----------------------------------
# Cargar variables del archivo .env
# ----------------------------------
load_dotenv()  
# Lee el archivo .env que está en la raíz del proyecto. Toma cada línea del tipo CLAVE=valor.
# Agrega esas claves y valores a os.environ, que es un diccionario especial de variables de entorno de Python.


#------------------------
# falta explicacion
#------------------------
app = Flask(__name__)


port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)





#--------------------------------------------------
# Busca dentro de os.environ la clave "SECRET_KEY"
#--------------------------------------------------
app.secret_key = os.environ.get("SECRET_KEY") 
# app.secret_key , "secret_key" es un atributo del objeto app
# Busca dentro de os.environ la clave "SECRET_KEY". Devuelve su valor (por ejemplo, 'ALVARO').
# Lo asigna a app.secret_key, que Flask usa para firmar las cookies de sesión
 




# ---------------------------------------
# Conexión a la base de datos MySQL
# ---------------------------------------
# Devuelve la conexión a la base de datos MySQL para la petición actual.
# Si no existe aún, la crea y la guarda en 'g' (un espacio temporal para la petición).
# Esto evita crear múltiples conexiones dentro de la misma petición.

# lo que estás haciendo es crear un objeto de tipo conexión (MySQLConnection) 
# Es una instancia de una clase provista por el conector mysql.connector, 
# que representa un canal abierto de comunicación entre tu aplicación y el servidor de base de datos MySQL.
def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(host="localhost",  #crea un objeto de tipo conexión (MySQLConnection) 
                                       user="alvaro", 
                                       password="apersichini86", 
                                       database="GestorPiezas")
    return g.db


 #--------------------------------
@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db:
        db.close()
 #-------------------------------




# Portal
#---------------------------------------------------------------------------------
@app.route("/portal")
def portal():
    if not session.get("user_id"):
        return redirect(url_for("login")) # Si no hay usuario logeado, redirecciona.

    db = get_db()
    cursor = db.cursor(dictionary=True) # → Crea un cursor, es otro objeto que permite enviar consultas SQL al servidor.
    cursor.execute("""
        SELECT p.id, p.nombre AS nombre, p.descripcion, p.codigo_interno
        FROM piezas p
        JOIN usuario_piezas up ON p.id = up.pieza_id
        WHERE up.usuario_id = %s """, (session.get("user_id"),))
    piezas = cursor.fetchall()
    cursor.close()

    return render_template("portal.html", piezas=piezas, usuario=session.get("username"))
#---------------------------------------------------------------------------------




# Login
#---------------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

      # "request" es un objeto global de Flask que representa la solicitud HTTP que hizo el navegador
    if request.method == "POST":

        # aca accede a los campos del formulario para poder validarlos
        email = request.form["email"]
        password = request.form["password"]



        db = get_db()



        # Objeto que se obtiene a partir de la conexión a la base de datos.
        # Permite ejecutar consultas SQL (SELECT, INSERT, etc.) y acceder a los resultados
        cursor = db.cursor(dictionary=True) # acá instancia el cursor, que es el objeto mapper.
        cursor.execute("SELECT * FROM usuarios WHERE email=%s AND contrasena=%s", (email, password))



      # fetchone()-------------------------------------
        user = cursor.fetchone()
      # Esta línea se usa después de ejecutar una consulta SQL con un cursor 
      # cursor.fetchone() recupera una sola fila del resultado de la consulta SQL.
      # Devuelve la primera fila pendiente del resultado como una tupla (o None si no hay más filas).
     

        cursor.close() # aca creo que hace un 'dispose' del objeto cursor

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["nombre"]
            session["is_admin"] = user["is_admin"]  
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for("portal"))
        else:
            flash("Credenciales inválidas", "error")

    return render_template("login.html")
#---------------------------------------------------------------------------------






# Registro 
# Acá procesa el formulario de registro, crea y almacena en BD el nuevo usuario
#---------------------------------------------------------------------------------
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor(dictionary=True) # aca vuelva a instanciar un cursor para poder hacer consultas SQL
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
#---------------------------------------------------------------------------------





# Logout
#---------------------------------------------------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
#---------------------------------------------------------------------------------







# Nueva Pieza
#---------------------------------------------------------------------------------
@app.route("/nueva", methods=["GET", "POST"])
def nueva_pieza():
    if not session.get("user_id"):  # Busca el valor asociado a "user_id" en el diccionario session
        return redirect(url_for("login"))

    if request.method == "POST": # Evalúa si la solicitud que llegó al servidor es tipo "POST"
        nombre = request.form["codigo"]
        descripcion = request.form["descripcion"]
        codigo_interno = request.form["categoria"]

        # llama a la base de datos y arma el objeto db y el objeto cursor, que es mapper
        db = get_db()
        cursor = db.cursor()

        # Insertar o ignorar pieza si ya existe
        # hace una consulta para ver si ya existe la pieza, 
        cursor.execute("SELECT id FROM piezas WHERE codigo_interno = %s", (codigo_interno,))
        pieza = cursor.fetchone() # crea una tupla, pieza es una tupla

        # ---------------------------------------------------------------------------------
        # Obs. En Python, para crear una tupla de un solo elemento, la coma es obligatoria.
        # t = (3,)
        # type(t)  # <class 'tuple'> 
        # La coma le dice a Python: “esto es una tupla, aunque tenga un solo elemento”.
        # ---------------------------------------------------------------------------------

        # Si ya existe una pieza con ese codigo_interno, obtiene su ID; si no, la crea.
        if pieza: # Cualquier objeto no nulo o no vacío es considerado True
            pieza_id = pieza[0] # accede al primer valor de la tupla, que es el ID de la pieza
           
        else:
            cursor.execute("INSERT INTO piezas (nombre, descripcion, codigo_interno) VALUES (%s, %s, %s)", (nombre, descripcion, codigo_interno))
            db.commit()
            pieza_id = cursor.lastrowid


        # Verificar si el usuario ya tiene esta pieza asociada
        # Insertar relación solo si no existe
        cursor.execute("""SELECT 1 FROM usuario_piezas WHERE usuario_id = %s AND pieza_id = %s""", (session.get("user_id"), pieza_id))
        relacion = cursor.fetchone()
        if not relacion:
         cursor.execute("""INSERT INTO usuario_piezas (usuario_id, pieza_id) VALUES (%s, %s)""", (session.get("user_id"), pieza_id))


        # hace el commit para subir los cambios a la BD
        db.commit()

        cursor.close() # hace el dispose del objeto

        return redirect(url_for("portal"))

    return render_template("nueva_pieza.html")

#---------------------------------------------------------------------------------





# Admin
#---------------------------------------------------------------------------------
@app.route("/admin")
def admin_panel():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    if not session.get("is_admin"):
        return "Acceso denegado", 403

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, email FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()

    return render_template("admin.html", usuarios=usuarios)

    

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
#---------------------------------------------------------------------------------






# Flask levanta el servidor
# --------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
# Este bloque asegura que el servidor Flask (app.run) solo se inicie
# cuando este archivo se ejecuta directamente con `python archivo.py`.
# Si este archivo se importa desde otro módulo, este bloque NO se ejecuta,
# lo que evita que se levante el servidor automáticamente.
#
# Además, app.run() inicia un bucle bloqueante (el servidor web),
# por lo tanto cualquier línea de código que esté debajo no se ejecutará
# hasta que se cierre el servidor (por ejemplo, con Ctrl+C).
#
# Es importante entender que:
# - Las definiciones de funciones, clases o rutas (usando `def`, `class`, `@app.route`) 
#   no se ejecutan, solo se cargan en memoria mientras Python lee el archivo.
# - En cambio, cualquier línea de código ejecutable como `print()`, 
#   llamadas a funciones, asignaciones o consultas a base de datos
#   se ejecuta en el momento en que Python la encuentra,
#   a menos que esté dentro de una función, clase o bloque condicional.
#
# Por eso, este `if` nos permite controlar *cuándo* y *cómo* se ejecuta el servidor
# y protege el resto de la lógica del programa.
# --------------------------------------------------------------------------------------
# debug=True es para hacer cambio con el servidor corriendo y actualizando la pagina
# se van viendo los cambios sin tener que reiniciar todo.





