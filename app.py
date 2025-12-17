import os
import uuid
from flask import Flask, render_template, request, send_file
from validador_cfdi import leer_datos_xml, validar_sat, generar_pdf

app = Flask(__name__)
UPLOADS = "uploads"
os.makedirs(UPLOADS, exist_ok=True)

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/")
def validar():
    f = request.files.get("xml")
    if not f or not f.filename.lower().endswith(".xml"):
        return "Sube un archivo .xml", 400

    xml_name = f"{uuid.uuid4()}.xml"
    xml_path = os.path.join(UPLOADS, xml_name)
    f.save(xml_path)

    datos = leer_datos_xml(xml_path)
    resp = validar_sat(datos)
    pdf_path = generar_pdf(datos, resp)

    # limpieza rápida
    try:
        os.remove(xml_path)
    except:
        pass

    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
