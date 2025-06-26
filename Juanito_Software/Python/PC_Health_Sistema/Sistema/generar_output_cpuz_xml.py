import re
import os
import subprocess
import xml.etree.ElementTree as ET
import os
import sys

# Establece el directorio actual al del script
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

TXT_REPORT = "cpuz_output"
XML_OUTPUT = "output.xml"

def generar_reporte_cpuz():
    """Ejecuta CPU-Z CLI para generar el fichero TXT."""
    if os.path.isfile("cpuz.exe"):
        try:
            subprocess.run(["cpuz.exe", f"-txt={TXT_REPORT}"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error ejecutando CPU-Z: {e}")
            sys.exit(1)
    else:
        print("No se encontró CPU-Z ejecutable en el directorio.")

def parsear_txt_cpuz(path):
    """Extrae los datos importantes desde el archivo TXT de CPU-Z."""
    datos = {}
    with open(path, encoding="latin-1") as f:
        texto = f.read()

    def buscar(pat, texto_a_buscar=None):
        if texto_a_buscar is None:
            texto_a_buscar = texto
        m = re.search(pat, texto_a_buscar, re.MULTILINE)
        return m.group(1).strip() if m else None


    # Extraemos CPU
    datos['Name']      = buscar(r"Name\s+(.+)")
    datos['CodeName']  = buscar(r"Codename\s+(.+)")
    datos['Revision']  = buscar(r"Core Stepping\s+(.+)")
    datos['Technology']= buscar(r"Technology\s+(.+)")

    """
    # Extraemos MAINBOARD (Placa Base) buscando patrón Mainboard y luego campos asociados
    mainboard_block = re.search(r"Mainboard\s*(.+?)(?:\n\n|\Z)", texto, re.DOTALL)
    if mainboard_block:
        mb_text = mainboard_block.group(1)
        # Para cada dato, extraemos la línea correspondiente:
        datos['Fabricante'] = buscar(r"Manufacturer:\s*(.+)", mb_text)
        datos['Modelo'] = buscar(r"Model:\s*(.+)", mb_text)
        datos['Bus Specs'] = buscar(r"Bus Specs:\s*(.+)", mb_text)
        datos['Chipset'] = buscar(r"Chipset:\s*(.+)", mb_text)
        datos['Southbridge'] = buscar(r"Southbridge:\s*(.+)", mb_text)
        datos['LPCIO'] = buscar(r"LPCIO:\s*(.+)", mb_text)
        datos['BIOS Brand'] = buscar(r"BIOS Brand:\s*(.+)", mb_text)
        datos['BIOS Version'] = buscar(r"BIOS Version:\s*(.+)", mb_text)
        datos['BIOS Date'] = buscar(r"BIOS Date:\s*(.+)", mb_text)
        datos['CPU Microcode'] = buscar(r"CPU Microcode:\s*(.+)", mb_text)
        datos['Graphic Interface Bus'] = buscar(r"Graphic Interface Bus:\s*(.+)", mb_text)
        datos['Current Link Width'] = buscar(r"Current Link Width:\s*(.+)", mb_text)
        datos['Max Supported Link Width'] = buscar(r"Max Supported Link Width:\s*(.+)", mb_text)
        datos['Current Link Speed'] = buscar(r"Current Link Speed:\s*(.+)", mb_text)
        datos['Max Supported Link Speed'] = buscar(r"Max Supported Link Speed:\s*(.+)", mb_text)
    """
    return datos

def generar_xml_cpuz(datos):
    """Genera un archivo XML llamado output.xml con los datos extraídos."""
    cpu = ET.Element("CPU")
    for clave, valor in datos.items():
        ET.SubElement(cpu, clave).text = valor if valor else "N/D"

    root = ET.Element("Hardware")
    root.append(cpu)

    tree = ET.ElementTree(root)
    tree.write(XML_OUTPUT, encoding="utf-8", xml_declaration=True)
    print(f"Archivo XML generado: {XML_OUTPUT}")

if __name__ == "__main__":
    generar_reporte_cpuz()
    archivo_txt = TXT_REPORT + ".txt"
    if os.path.exists(archivo_txt):
        datos = parsear_txt_cpuz(archivo_txt)
        generar_xml_cpuz(datos)
    else:
        print("No se generó el archivo TXT correctamente.")
