import xml.etree.ElementTree as ET
from zeep import Client
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

def leer_datos_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    ns = {
        "cfdi": "http://www.sat.gob.mx/cfd/4",
        "tfd": "http://www.sat.gob.mx/TimbreFiscalDigital"
    }

    emisor = root.find(".//cfdi:Emisor", ns)
    receptor = root.find(".//cfdi:Receptor", ns)
    timbre = root.find(".//tfd:TimbreFiscalDigital", ns)

    if timbre is None:
        raise Exception("El XML no contiene TimbreFiscalDigital")

    uuid = timbre.attrib.get("UUID", "").upper()
    rfc_emisor = emisor.attrib.get("Rfc", "") if emisor is not None else ""
    rfc_receptor = receptor.attrib.get("Rfc", "") if receptor is not None else ""

    if not all([uuid, rfc_emisor, rfc_receptor]):
        raise Exception("No se pudieron extraer UUID/RFCs del XML")

    total = f"{float(root.attrib.get('Total', 0)):.6f}"

    tipo = root.attrib.get("TipoDeComprobante", "")
    efecto_map = {"I":"Ingreso","E":"Egreso","T":"Traslado","N":"Nómina","P":"Pago"}
    efecto = efecto_map.get(tipo, "")

    nombre_emisor = emisor.attrib.get("Nombre", "") if emisor is not None else ""
    nombre_receptor = receptor.attrib.get("Nombre", "") if receptor is not None else ""

    fecha_expedicion = root.attrib.get("Fecha", "")
    fecha_certificacion = timbre.attrib.get("FechaTimbrado", "")
    pac = timbre.attrib.get("RfcProvCertif", "")

    return {
        "uuid": uuid,
        "re": rfc_emisor,
        "rr": rfc_receptor,
        "tt": total,
        "efecto": efecto,
        "nombre_emisor": nombre_emisor,
        "nombre_receptor": nombre_receptor,
        "fecha": fecha_expedicion,
        "fecha_cert": fecha_certificacion,
        "pac": pac
    }

def validar_sat(datos):
    wsdl = "https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc?wsdl"
    client = Client(wsdl)

    expresion = (
        f"?id={datos['uuid']}"
        f"&re={datos['re']}"
        f"&rr={datos['rr']}"
        f"&tt={datos['tt']}"
    )

    return client.service.Consulta(expresionImpresa=expresion)

def generar_pdf(datos, respuesta):
    nombre_pdf = f"Validacion_{datos['uuid']}.pdf"

    doc = SimpleDocTemplate(
        nombre_pdf,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph(
        "<b>Verificación de comprobantes fiscales digitales por internet</b>",
        styles["Title"]
    ))
    elementos.append(Spacer(1, 25))

    tabla1 = Table([
        ["RFC del emisor", "Nombre o razón social del emisor",
         "RFC del receptor", "Nombre o razón social del receptor"],
        [
            datos["re"],
            Paragraph(datos.get("nombre_emisor",""), styles["Normal"]),
            datos["rr"],
            Paragraph(datos.get("nombre_receptor",""), styles["Normal"]),
        ]
    ], colWidths=[90, 190, 90, 190])

    tabla1.setStyle(TableStyle([
        ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 6),
        ("TOPPADDING", (0,1), (-1,1), 6),
    ]))

    elementos.append(tabla1)
    elementos.append(Spacer(1, 18))

    tabla2 = Table([
        ["Folio fiscal", "Fecha de expedición",
         "Fecha certificación SAT", "PAC que certificó"],
        [
            Paragraph(datos["uuid"], styles["Normal"]),
            datos.get("fecha",""),
            datos.get("fecha_cert",""),
            datos.get("pac","")
        ]
    ], colWidths=[200, 110, 130, 120])

    tabla2.setStyle(TableStyle([
        ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 6),
        ("TOPPADDING", (0,1), (-1,1), 6),
    ]))

    elementos.append(tabla2)
    elementos.append(Spacer(1, 18))

    tabla3 = Table([
        ["Total del CFDI", "Efecto del comprobante",
         "Estado CFDI", "Estatus de cancelación"],
        [
            f"${float(datos['tt']):,.2f}",
            datos.get("efecto",""),
            getattr(respuesta, "Estado", ""),
            getattr(respuesta, "EstatusCancelacion", "")
        ]
    ], colWidths=[100, 160, 120, 180])

    tabla3.setStyle(TableStyle([
        ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 6),
        ("TOPPADDING", (0,1), (-1,1), 6),
    ]))

    elementos.append(tabla3)
    elementos.append(Spacer(1, 30))

    elementos.append(Paragraph(
        "<font size=9>"
        "Documento informativo generado mediante consulta al WebService oficial del SAT. "
        "La validez del CFDI depende del estado reportado por el SAT al momento de la consulta."
        "</font>",
        styles["Normal"]
    ))

    doc.build(elementos)
    return nombre_pdf
