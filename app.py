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

client = gspread.service_account(filename=tmp_path)
sheet = client.open("ControlAsistencia").sheet1
empleados_sheet = client.open("ControlAsistencia").worksheet("Empleados")



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
    empleados = empleados_sheet.col_values(1)
    opciones = "".join([f'<option value="{e}">{e}</option>' for e in empleados if e])
    return f'''
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Control de Asistencia</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#f0f4f8;min-height:100vh;display:flex;align-items:center;justify-content:center;font-family:sans-serif;padding:1rem}}
.card{{background:white;border-radius:20px;padding:2.5rem 2rem;width:100%;max-width:420px;border:1px solid #e2e8f0}}
.logo{{width:64px;height:64px;border-radius:16px;background:#1a56db;display:flex;align-items:center;justify-content:center;margin:0 auto 1.5rem}}
.logo i{{font-size:32px;color:white}}
h1{{font-size:22px;font-weight:500;text-align:center;color:#1a202c;margin-bottom:0.25rem}}
.sub{{font-size:14px;color:#718096;text-align:center;margin-bottom:2rem}}
label{{font-size:13px;color:#4a5568;font-weight:500;display:block;margin-bottom:6px}}
select{{width:100%;padding:14px 16px;border:1px solid #e2e8f0;border-radius:12px;font-size:16px;color:#1a202c;outline:none;background:white;appearance:none}}
select:focus{{border-color:#1a56db}}
.btn{{width:100%;padding:16px;background:#1a56db;color:white;border:none;border-radius:12px;font-size:16px;font-weight:500;margin-top:1.25rem;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px}}
.result{{margin-top:1.25rem;padding:14px 16px;border-radius:12px;font-size:15px;font-weight:500;text-align:center;display:none}}
.entrada{{background:#ebf8f0;color:#276749;border:1px solid #9ae6b4}}
.salida{{background:#fff5e6;color:#7b4d12;border:1px solid #fbd38d}}
.completado{{background:#e6f0ff;color:#1a3a7a;border:1px solid #90b4fa}}
.time{{font-size:12px;color:#a0aec0;text-align:center;margin-top:1.5rem}}
</style>
</head>
<body>
<div class="card">
  <div class="logo"><i class="ti ti-clipboard-check"></i></div>
  <h1>Control de Asistencia</h1>
  <p class="sub">Selecciona tu nombre</p>
  <label for="nombre">Nombre</label>
  <select id="nombre">
    <option value="">-- Selecciona tu nombre --</option>
    {opciones}
  </select>
  <button class="btn" onclick="registrar()">
    <i class="ti ti-fingerprint"></i> Registrar entrada / salida
  </button>
  <div class="result" id="resultado"></div>
  <p class="time" id="reloj"></p>
</div>
<script>
function pad(n){{return String(n).padStart(2,'0')}}
function tick(){{const n=new Date();document.getElementById('reloj').textContent=pad(n.getDate())+'/'+pad(n.getMonth()+1)+'/'+n.getFullYear()+'  ·  '+pad(n.getHours())+':'+pad(n.getMinutes())+':'+pad(n.getSeconds())}}
tick();setInterval(tick,1000);
function registrar(){{
  const nombre=document.getElementById('nombre').value;
  if(!nombre){{alert('Por favor selecciona tu nombre');return}}
  const res=document.getElementById('resultado');
  res.style.display='block';res.className='result';res.textContent='Registrando...';
  fetch('/check?user='+encodeURIComponent(nombre))
  .then(r=>r.text()).then(t=>{{
    res.style.display='block';
    if(t.includes('Entrada')){{res.className='result entrada';res.innerHTML='✅ '+t}}
    else if(t.includes('Salida')){{res.className='result salida';res.innerHTML='🕐 '+t}}
    else{{res.className='result completado';res.innerHTML='ℹ️ '+t}}
    document.getElementById('nombre').value='';
  }});
}}
</script>
</body>
</html>
'''
    





# ------------ ARRANQUE ----------- #
if __name__ == "__main__":
    app.run(debug=True)
