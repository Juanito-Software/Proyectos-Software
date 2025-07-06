# Copyright (C) 2025 Juanito Software
#
# Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo
# los términos de la Licencia Pública General de GNU publicada por la Free
# Software Foundation, ya sea la versión 3 de la Licencia o (según tu elección)
# cualquier versión posterior.
#
# Este programa se distribuye con la esperanza de que sea útil, pero SIN
# NINGUNA GARANTÍA; incluso sin la garantía implícita de COMERCIALIZACIÓN o
# IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Consulta la Licencia Pública General
# de GNU para más detalles.
#
# Deberías haber recibido una copia de la Licencia Pública General de GNU junto
# con este programa. Si no es así, visita <https://www.gnu.org/licenses/>.

# Este proyecto usa FFmpeg, que está licenciado bajo GPLv3.
# Para más información, visita https://ffmpeg.org/legal.html
# Se respetan todos los derechos y avisos de copyright de FFmpeg. 

import os
import subprocess
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QApplication
import sys

class FFmpegConverter(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("converter.ui", self)

        self.btnOrigen.clicked.connect(self.select_input_folder)
        self.btnDestino.clicked.connect(self.select_output_folder)
        self.btnConvert.clicked.connect(self.convert_files)

        self.input_folder = ""
        self.output_folder = ""

        # Lista de formatos de audio que quieres soportar
        self.audio_formats = {
            "aac", "ac3", "ac4", "aiff", "alaw", "ape", "atrac1", "atrac3", "caf", "dts", "dtshd",
            "flac", "gsm", "ilbc", "m4a", "mlp", "mp3", "mpc", "mpc8", "opus", "ra", "tak", "tta",
            "wav", "wma", "wv", "sbc", "shn", "vqf", "w64", "amr", "amrnb", "amrwb", "adx", "g722",
            "g723_1", "g726", "g726le", "g729", "libgme", "libmodplug", "libopenmpt", "loas", "lrc",
            "mid", "midi"
        }

        # Detectar formatos disponibles
        formats = self.audio_formats
        self.cmbInput.addItems(formats)
        self.cmbOutput.addItems(formats)

    def select_input_folder(self):
        self.input_folder = QFileDialog.getExistingDirectory(self, "Selecciona carpeta de origen")
        self.txtLog.append(f"📁 Carpeta de origen: {self.input_folder}")

    def select_output_folder(self):
        self.output_folder = QFileDialog.getExistingDirectory(self, "Selecciona carpeta de destino")
        self.txtLog.append(f"📁 Carpeta de destino: {self.output_folder}")

    def convert_files(self):
        input_ext = self.cmbInput.currentText()
        output_ext = self.cmbOutput.currentText()

        if not self.input_folder or not self.output_folder:
            self.txtLog.append("❌ Debes seleccionar ambas carpetas.")
            return

        files = [f for f in os.listdir(self.input_folder) if f.lower().endswith(f".{input_ext}")]
        if not files:
            self.txtLog.append("⚠️ No se encontraron archivos con esa extensión.")
            return

        # Determinar la ruta de ffmpeg
        if is_ffmpeg_available():
            ffmpeg_cmd = "ffmpeg"
        else:
            ffmpeg_cmd = resource_path("ffmpeg/ffmpeg.exe")  # versión local

        for f in files:
            input_path = os.path.join(self.input_folder, f)
            output_name = os.path.splitext(f)[0] + f".{output_ext}"
            output_path = os.path.join(self.output_folder, output_name)

            cmd = [ffmpeg_cmd, "-y", "-i", input_path, output_path]

            try:
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                self.txtLog.append(f"✅ {f} → {output_name}")
            except subprocess.CalledProcessError as e:
                self.txtLog.append(f"❌ Error: {f}\n{e.stderr.decode()}")

    def get_ffmpeg_formats(self):
        result = subprocess.run(["ffmpeg", "-hide_banner", "-formats"],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        lines = result.stdout.decode().splitlines()
        formats = set()
        for line in lines:
            if line.startswith(" D") or line.startswith(" E") or line.startswith(" DE"):
                parts = line.split()
                if len(parts) >= 2:
                    formats.add(parts[1])
        return sorted(list(formats))

def is_ffmpeg_available():
    """Comprueba si ffmpeg está en el PATH del sistema."""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except Exception:
        base_path = os.path.abspath(".")  # ejecución normal

    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = FFmpegConverter()
    ventana.show()
    sys.exit(app.exec_())
