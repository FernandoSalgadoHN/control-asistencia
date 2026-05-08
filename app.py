from flask import Flask, request
import gspread
from datetime import datetime

app = Flask(__name__)



# -------- GOOGLE SHEETS --------#

"""
client = gspread.service_account(filename="credenciales.json")
"""
import os, json, tempfile
creds_json = os.environ.get("GOOGLE_CREDENTIALS")
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    f.write(creds_json)
    tmp_path = f.name

client = gspread.service_account(filename-tmp_path)
sheet = client.open("ControlAsistencia").sheet1



# ---------- FUNCIONES ----------- #
def registrar(nombre):
    now = datetime.now()
    fecha = now.strftime("%Y-%m-%d")
    hora = now.strftime("%H:%M:%S")

    registros = sheet.get_all_records()

    # Buscar registro de hoy
    for i, row in enumerate(registros):
        if row["Nombre"] == nombre and row["Fecha"] == fecha:
            if row["Salida"] == "":
                sheet.update_cell(i+2, 4, hora)
                return "Salida registrada"
            else:
                return "Ya completado hoy"
            
    #Si no existe > nueva entrada
    sheet.append_row([nombre, fecha, hora, ""])
    return "Entrada registrada"


# ------------- RUTAS ------------ #
@app.route("/")
def inicio():
    return "Servidor funcionando"

@app.route("/check")
def check():
    nombre = request.args.get("user")

    if not nombre:
        return "Usuario no especificado"
    
    resultado = registrar(nombre)
    return f"{resultado} - {nombre}"




# --------- HTML SIMPLE --------- #
@app.route("/registro")
def registro():
    return '''
    <html>
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width-device-width">
    <title>Control Asistencia</title>
    </head>
    <body style="text-align:center; font-family:sans-serif; padding:40px">
    <h2>Control Asistencia</h2>
    <input id="nombre" placeholder="Tu nombre completo"
            style="padding:10px; font-size:18px; width:80%><br><br>
    <button onclick="registar()"
            style="padding:15px 30px; font-size:18px; background:green; color:white; border:name; border-radius:8px"
        Registrar entrada/salida</button>
    <p id="resultado"></p>
    <script>
    function registrar() {
        const nombre = document.getElementById("nombre").value;
        if (!nombre) { alert("Escribe tu nombre"); return; }
        fetch("/check?user=" + encodeURIComponent(nomnre))
        .then(r => r.text())
        .then(t => document.getElementById("resultado").innerText = t);

    }
    </script>
    </body>
    </html>
    '''
    





# ------------ ARRANQUE ----------- #
if __name__ == "__main__":
    app.run(debug=True)
