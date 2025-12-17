import os
import uuid
import zipfile
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
    xmls = request.files.getlist("xmls")
    if not xmls or len(xmls) == 0:
        return "No se subieron archivos", 400

    # (opcional) límite
    if len(xmls) > 10:
        return "Máximo 10 XML por validación", 400

    run_id = str(uuid.uuid4())
    run_dir = os.path.join(UPLOADS, run_id)
    os.makedirs(run_dir, exist_ok=True)

    pdfs_generados = []
    xml_paths = []

    try:
        # Procesar todos los XMLs
        for f in xmls:
            if not f.filename.lower().endswith(".xml"):
                continue

            xml_name = f"{uuid.uuid4()}.xml"
            xml_path = os.path.join(run_dir, xml_name)
            f.save(xml_path)
            xml_paths.append(xml_path)

            datos = leer_datos_xml(xml_path)
            resp = validar_sat(datos)
            pdf_path = generar_pdf(datos, resp)  # genera PDF (como ya lo tienes)
            pdfs_generados.append(pdf_path)

        if len(pdfs_generados) == 0:
            return "No se pudo generar ningún PDF", 400

        # ✅ SI ES SOLO 1 → DEVOLVER PDF
        if len(pdfs_generados) == 1:
            return send_file(pdfs_generados[0], as_attachment=True)

        # ✅ SI SON VARIOS → DEVOLVER ZIP
        zip_path = os.path.join(run_dir, "validaciones_cfdi.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for pdf in pdfs_generados:
                zipf.write(pdf, arcname=os.path.basename(pdf))

        return send_file(zip_path, as_attachment=True)

    finally:
        # Limpieza de XML subidos
        for p in xml_paths:
            try:
                os.remove(p)
            except:
                pass

        # Limpieza de PDFs generados (para que no se acumulen)
        for pdf in pdfs_generados:
            try:
                os.remove(pdf)
            except:
                pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
