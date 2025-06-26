# Copyright (C) 2025 JuanitoSoftware&Games
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

import tkinter as tk
import platform
import psutil
import shutil
import GPUtil
import wmi
from cpuinfo import get_cpu_info
import xml.etree.ElementTree as ET
import os
import traceback
from tkinter import messagebox
import sys
import threading
import time
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, as_completed
import weakref
import atexit
import signal
import sys
import logging
import psutil
import platform
import subprocess
import GPUtil
from tabulate import tabulate
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
import subprocess
import sys
import threading

logging.basicConfig(filename='log_ejecucion.txt', level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.debug('Arrancando programa')

def resource_path(relative):
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative)

xml_path = resource_path("output.xml")

matrix_effect_run = False
matrix_effect_lock = threading.Lock()

def run_matrix_effect():
    global matrix_effect_run

    with matrix_effect_lock:
        if matrix_effect_run:
            return
        matrix_effect_run = True

    # Fuera del lock para no bloquear mientras ejecuta el programa externo
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(base_path, "matrix_effect.exe")

    try:
        subprocess.run([exe_path], check=True)
    except Exception as e:
        with matrix_effect_lock:
            matrix_effect_run = False
        print(f"Error ejecutando matrix_effect.exe: {e}")

class SystemInfoManager:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="SysInfo")
        self.shutdown_event = threading.Event()
        self.active_tasks = []
        self._cleanup_registered = False
        self._data_requested = False
        
    def register_cleanup(self):
        """Registra la limpieza automática al cerrar la aplicación"""
        if not self._cleanup_registered:
            atexit.register(self.cleanup)
            self._cleanup_registered = True
    
    def submit_task(self, func, *args, **kwargs):
        """Envía una tarea al pool de hilos"""
        if self.shutdown_event.is_set():
            return None
        
        future = self.executor.submit(func, *args, **kwargs)
        self.active_tasks.append(weakref.ref(future))
        return future
    
    def cleanup(self):
        """Limpia recursos y termina hilos correctamente"""
        if self.shutdown_event.is_set():
            return
            
        print("Iniciando limpieza de hilos...")
        self.shutdown_event.set()
        
        try:
            # Cancelar tareas pendientes
            cancelled_count = 0
            for task_ref in self.active_tasks:
                task = task_ref()
                if task and not task.done():
                    if task.cancel():
                        cancelled_count += 1
            
            print(f"Tareas canceladas: {cancelled_count}")
            
            # Cerrar el executor sin timeout ni espera activa
            print("Cerrando executor...")
            self.executor.shutdown(wait=True)
            
            print("Limpieza de hilos completada")
            
        except Exception as e:
            print(f"Error durante limpieza: {e}")
            # Si hay error, intentar marcar shutdown como True
            try:
                self.executor._shutdown = True
            except Exception:
                pass


# Instancia global del manager
system_manager = SystemInfoManager()

def com_initialized(func):
    def wrapper(*args, **kwargs):
        import pythoncom
        pythoncom.CoInitialize()
        try:
            return func(*args, **kwargs)
        finally:
            pythoncom.CoUninitialize()
    return wrapper

def obtener_datos_placa_base():
    """Obtiene información detallada de la placa base desde XML"""
    if system_manager.shutdown_event.is_set():
        return {}
        
    datos = {}
    try:
        if not os.path.exists(xml_path):
            return {}
            
        tree = ET.parse(xml_path)
        root = tree.getroot()
        mainboard = root.find("Mainboard")
        
        if mainboard is not None:
            # Mapeo de campos XML a nombres legibles
            campos = {
                'Manufacturer': 'Fabricante',
                'Model': 'Modelo',
                'BusSpecs': 'Bus Specs'
            }
            
            for xml_field, display_name in campos.items():
                valor = mainboard.findtext(xml_field)
                if valor:
                    datos[display_name] = valor
            
            # Chipset
            chipset = mainboard.find("Chipset")
            if chipset is not None:
                chipset_name = chipset.text
                chipset_rev = chipset.get("rev")
                if chipset_name:
                    datos['Chipset'] = f"{chipset_name} Rev. {chipset_rev if chipset_rev else 'N/A'}"
            
            # Southbridge
            southbridge = mainboard.find("Southbridge")
            if southbridge is not None:
                sb_name = southbridge.text
                sb_rev = southbridge.get("rev")
                if sb_name:
                    datos['Southbridge'] = f"{sb_name} Rev. {sb_rev if sb_rev else 'N/A'}"
            
            # BIOS
            bios = mainboard.find("BIOS")
            if bios is not None:
                bios_campos = {
                    'Brand': 'BIOS Brand',
                    'Version': 'BIOS Version',
                    'Date': 'BIOS Date',
                    'CPU Microcode': 'CPU Microcode'
                }
                
                for xml_field, display_name in bios_campos.items():
                    valor = bios.findtext(xml_field)
                    if valor:
                        datos[display_name] = valor
        
    except Exception as e:
        print(f"Error leyendo placa base desde XML: {e}")
    
    return datos

def obtener_datos_placa_base_2():
    datos = {}
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        mainboard = root.find("Mainboard")

        if mainboard is not None:
            def add_if_not_none(clave, valor):
                if valor: datos[clave] = valor

            add_if_not_none('Fabricante', mainboard.findtext("Manufacturer"))
            add_if_not_none('Modelo', mainboard.findtext("Model"))
            add_if_not_none('Bus Specs', mainboard.findtext("BusSpecs"))

            chipset = mainboard.find("Chipset")
            if chipset is not None:
                add_if_not_none('Chipset', f"{chipset.text} Rev. {chipset.get('rev', 'N/A')}")

            southbridge = mainboard.find("Southbridge")
            if southbridge is not None:
                add_if_not_none('Southbridge', f"{southbridge.text} Rev. {southbridge.get('rev', 'N/A')}")

            lpcio = mainboard.find("LPCIO")
            if lpcio is not None:
                add_if_not_none('LPCIO', f"{lpcio.text} {lpcio.get('model', '')}")

            bios = mainboard.find("BIOS")
            if bios is not None:
                add_if_not_none('BIOS Brand', bios.findtext("Brand"))
                add_if_not_none('BIOS Version', bios.findtext("Version"))
                add_if_not_none('BIOS Date', bios.findtext("Date"))
                add_if_not_none('CPU Microcode', bios.findtext("CPU Microcode"))

            gi = mainboard.find("Graphic_Interface")
            if gi is not None:
                add_if_not_none('Graphic Interface Bus', gi.findtext("Bus"))
                add_if_not_none('Current Link Width', gi.findtext("Current_Link_Width"))
                add_if_not_none('Max Supported Link Width', gi.findtext("Max_Supported_Link_Width"))
                add_if_not_none('Current Link Speed', gi.findtext("Current_Link_Speed"))
                add_if_not_none('Max Supported Link Speed', gi.findtext("Max_Supported_Link_Speed"))
    except Exception as e:
        return {'Error Placa Base': str(e)}
    return datos

def obtener_datos_placa_base_3():
    datos = {}
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        mainboard = root.find("Mainboard")
        if mainboard is not None:
            # Extraemos cada campo si existe
            manufacturer = mainboard.findtext("Manufacturer")
            model = mainboard.findtext("Model")
            bus_specs = mainboard.findtext("BusSpecs")
            
            chipset = mainboard.find("Chipset")
            chipset_name = chipset.text if chipset is not None else None
            chipset_rev = chipset.get("rev") if chipset is not None else None
            
            southbridge = mainboard.find("Southbridge")
            southbridge_name = southbridge.text if southbridge is not None else None
            southbridge_rev = southbridge.get("rev") if southbridge is not None else None
            
            lpcio = mainboard.find("LPCIO")
            lpcio_name = lpcio.text if lpcio is not None else None
            lpcio_model = lpcio.get("model") if lpcio is not None else None
            
            bios = mainboard.find("BIOS")
            bios_brand = bios.findtext("Brand") if bios is not None else None
            bios_version = bios.findtext("Version") if bios is not None else None
            bios_date = bios.findtext("Date") if bios is not None else None
            bios_microcode = bios.findtext("CPU Microcode") if bios is not None else None
            
            graphic_interface = mainboard.find("Graphic_Interface")
            gi_bus = graphic_interface.findtext("Bus") if graphic_interface is not None else None
            gi_current_link_width = graphic_interface.findtext("Current_Link_Width") if graphic_interface is not None else None
            gi_max_supported_link_width = graphic_interface.findtext("Max_Supported_Link_Width") if graphic_interface is not None else None
            gi_current_link_speed = graphic_interface.findtext("Current_Link_Speed") if graphic_interface is not None else None
            gi_max_supported_link_speed = graphic_interface.findtext("Max_Supported_Link_Speed") if graphic_interface is not None else None
            
            # Guardamos en el dict solo si no son None para evitar campos vacíos
            if manufacturer:
                datos['Fabricante'] = manufacturer
            if model:
                datos['Modelo'] = model
            if bus_specs:
                datos['Bus Specs'] = bus_specs
            if chipset_name:
                datos['Chipset'] = f"{chipset_name} Rev. {chipset_rev if chipset_rev else 'N/A'}"
            if southbridge_name:
                datos['Southbridge'] = f"{southbridge_name} Rev. {southbridge_rev if southbridge_rev else 'N/A'}"
            if lpcio_name:
                datos['LPCIO'] = f"{lpcio_name} {lpcio_model if lpcio_model else ''}"
            if bios_brand:
                datos['BIOS Brand'] = bios_brand
            if bios_version:
                datos['BIOS Version'] = bios_version
            if bios_date:
                datos['BIOS Date'] = bios_date
            if bios_microcode:
                datos['CPU Microcode'] = bios_microcode
            if gi_bus:
                datos['Graphic Interface Bus'] = gi_bus
            if gi_current_link_width:
                datos['Current Link Width'] = gi_current_link_width
            if gi_max_supported_link_width:
                datos['Max Supported Link Width'] = gi_max_supported_link_width
            if gi_current_link_speed:
                datos['Current Link Speed'] = gi_current_link_speed
            if gi_max_supported_link_speed:
                datos['Max Supported Link Speed'] = gi_max_supported_link_speed

    except Exception as e:
        print("Error al obtener datos de la placa base "+e)
        return {'Error Placa Base': str(e)}
    return datos

def obtener_datos_cpu_extra():
    """Obtiene información adicional del CPU usando py-cpuinfo"""
    if system_manager.shutdown_event.is_set():
        return None
        
    try:
        cpu_info = get_cpu_info()
        datos = {
            'Nombre (py-cpuinfo)': cpu_info.get('brand_raw', 'N/A'),
            'Arquitectura': cpu_info.get('arch', 'N/A'),
            'Bits': cpu_info.get('bits', 'N/A'),
        }
        
        # Instrucciones soportadas (solo algunas para no sobrecargar)
        flags = cpu_info.get('flags', [])
        if flags:
            datos['Instrucciones soportadas'] = ', '.join(flags[:10]) + "..."
        
        # Información de caché si está disponible
        if 'l2_cache_size' in cpu_info:
            datos['Caché L2'] = cpu_info.get('l2_cache_size')
        if 'l3_cache_size' in cpu_info:
            datos['Caché L3'] = cpu_info.get('l3_cache_size')
            
        return datos
    except Exception as e:
        print(f"Error obteniendo info CPU: {e}")
        return {'Error CPU Info': str(e)}

def obtener_datos_cpuz():
    """Obtiene datos del archivo XML de CPU-Z"""
    if system_manager.shutdown_event.is_set():
        return {}
        
    datos = {}
    try:
        if not os.path.exists(xml_path):
            return {'CPU-Z XML': "Archivo no encontrado"}
            
        tree = ET.parse(xml_path)
        root = tree.getroot()
        cpu = root.find("CPU")
        
        if cpu is not None:
            datos['Nombre (CPU-Z)'] = cpu.findtext("Name", "N/A")
            datos['Nombre en clave'] = cpu.findtext("CodeName", "N/A")
            datos['Tecnología'] = cpu.findtext("Technology", "N/A")
            datos['Revisión'] = cpu.findtext("Revision", "N/A")
        else:
            datos['CPU-Z XML'] = "Sección CPU no encontrada"
            
    except Exception as e:
        datos['CPU-Z XML'] = f"Error al leer: {str(e)}"
    return datos

def obtener_datos_cpuz():
    datos = {}
    try:
        if not os.path.exists(xml_path):
            return {'CPU-Z XML': "Archivo no encontrado"}

        tree = ET.parse(xml_path)
        root = tree.getroot()
        cpu = root.find("CPU")

        if cpu is not None:
            datos['Nombre (CPU-Z)'] = cpu.findtext("Name", "N/A")
            datos['Nombre en clave'] = cpu.findtext("CodeName", "N/A")
            datos['Tecnología'] = cpu.findtext("Technology", "N/A")
            datos['Revisión'] = cpu.findtext("Revision", "N/A")
        else:
            datos['CPU-Z XML'] = "Sección CPU no encontrada"
    except Exception as e:
        datos['CPU-Z XML'] = f"Error al leer: {str(e)}"
    return datos


def obtener_info_basica():
    try:
        return {
            'Identidad': {
                'Nombre del dispositivo': platform.node()
            },
            'Sistema Operativo': {
                'Sistema operativo': platform.system() + " " + platform.release()
            },
            'Arquitectura': {
                'Arquitectura': platform.machine()
            }
        }
    except Exception as e:
        return {"Error": str(e)}

@com_initialized
def obtener_info_procesador():
    try:
        info_proc = {}
        w = wmi.WMI()

        for cpu in w.Win32_Processor():
            info_proc['Procesador'] = cpu.Name.strip()
            info_proc['Velocidad (GHz)'] = f"{float(cpu.MaxClockSpeed) / 1000:.2f} GHz"
            info_proc['ID'] = cpu.ProcessorId
            info_proc['L2 WMI'] = f"{cpu.L2CacheSize} KB"
            info_proc['L3 WMI'] = f"{cpu.L3CacheSize} KB"
            info_proc['Socket'] = cpu.SocketDesignation

            tdp = getattr(cpu, 'ThermalDesignPower', None)
            info_proc['Max TDP (W)'] = f"{tdp} W" if tdp else "No disponible"

            core_voltage = getattr(cpu, 'CurrentVoltage', None)
            if core_voltage and core_voltage > 128:
                volt = (core_voltage - 128) / 10
                info_proc['Core Voltage (V)'] = f"{volt:.2f} V"
            elif core_voltage:
                info_proc['Core Voltage'] = f"{core_voltage} (valor codificado)"
            else:
                info_proc['Core Voltage'] = "No disponible"
            break

        info_proc['Núcleos físicos'] = psutil.cpu_count(logical=False)
        info_proc['Núcleos lógicos (hilos)'] = psutil.cpu_count(logical=True)
        info_proc['Familia Procesador'] = platform.processor()

        return info_proc
    except Exception as e:
        return {'Error Procesador': str(e)}

def obtener_info_memoria():
    try:
        ram = psutil.virtual_memory()
        info = {
            'RAM instalada': f"{round(ram.total / (1024 ** 3), 2)} GB",
            'RAM disponible': f"{round(ram.available / (1024 ** 3), 2)} GB"
        }

        if platform.system() == "Windows":
            try:
                output = subprocess.check_output(
                    ['wmic', 'MemoryChip', 'get', 'Capacity,Manufacturer,MemoryType,Speed,PartNumber,ConfiguredVoltage', '/format:list'],
                    universal_newlines=True
                )
                
                chips = output.strip().split("\n\n")
                
                for idx, chip in enumerate(chips, start=1):
                    for line in chip.strip().split("\n"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            clave = f"{key.strip()}_{idx}"
                            info[clave] = value.strip()

            except Exception as e:
                info['Error detalles RAM'] = f"No se pudo obtener información detallada: {e}"

        return info

    except Exception as e:
        return {'Error Memoria': str(e)}

def obtener_datos_cpu_extra():
    try:
        cpu_info = get_cpu_info()
        datos = {
            'Nombre (py-cpuinfo)': cpu_info.get('brand_raw', 'N/A'),
            'Arquitectura': cpu_info.get('arch', 'N/A'),
            'Bits': cpu_info.get('bits', 'N/A'),
        }

        flags = cpu_info.get('flags', [])
        if flags:
            datos['Instrucciones soportadas'] = ', '.join(flags[:10]) + "..."

        if 'l2_cache_size' in cpu_info:
            datos['Caché L2'] = cpu_info.get('l2_cache_size')
        if 'l3_cache_size' in cpu_info:
            datos['Caché L3'] = cpu_info.get('l3_cache_size')

        return datos
    except Exception as e:
        return {'Error CPU Info': str(e)}

def obtener_info_almacenamiento():
    """Obtiene información de almacenamiento"""
    if system_manager.shutdown_event.is_set():
        return {}
        
    try:
        total, used, free = shutil.disk_usage("/")
        return {
            'Almacenamiento total': f"{round(total / (1024 ** 4), 2)} TB",
            'Almacenamiento usado': f"{round(used / (1024 ** 4), 2)} TB",
            'Almacenamiento libre': f"{round(free / (1024 ** 4), 2)} TB"
        }
    except Exception as e:
        print(f"Error obteniendo info almacenamiento: {e}")
        return {'Error Almacenamiento': str(e)}

@com_initialized
def obtener_info_placa_base():
    """Obtiene información de la placa base combinando XML y WMI"""
    if system_manager.shutdown_event.is_set():
        return {}

    try:
        # Inicializamos datos como diccionario vacío
        datos = {}

        # Intentamos obtener datos desde distintas fuentes XML
        fuentes = [
            obtener_datos_placa_base,
            obtener_datos_placa_base_2,
            obtener_datos_placa_base_3
        ]

        for fuente in fuentes:
            nuevos_datos = fuente()
            if nuevos_datos:
                # Añadir solo claves con valores no nulos
                datos.update({k: v for k, v in nuevos_datos.items() if v})

        # Si sigue vacío tras todas las fuentes, usar WMI como respaldo
        if not datos:
            w = wmi.WMI()
            for board in w.Win32_BaseBoard():
                datos = {
                    'Modelo de placa base': board.Product or "No disponible"
                }
                break

        return datos

    except Exception as e:
        print(f"Error obteniendo info placa base: {e}")
        return {'Error Placa Base': str(e)}


def obtener_info_gpu():
    """Obtiene información de la tarjeta gráfica en formato plano estilo RAM"""
    if system_manager.shutdown_event.is_set():
        return {}

    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if not gpus:
            return {'Tarjeta gráfica': 'No detectada'}

        info = {}
        for idx, gpu in enumerate(gpus, start=1):
            info[f"ID"] = gpu.id
            info[f"Nombre"] = gpu.name
            info[f"Uso_GPU"] = f"{gpu.load * 100:.1f}%"
            info[f"Memoria_GPU"] = f"{gpu.memoryUsed}MB / {gpu.memoryTotal}MB"
            info[f"Temperatura_GPU"] = f"{gpu.temperature} °C"
            info[f"Driver"] = gpu.driver

        return info

    except Exception as e:
        return {'Error GPU': str(e)}


@com_initialized
def obtener_info_so_detallada():
    """Obtiene información detallada del SO usando WMI"""
    if system_manager.shutdown_event.is_set():
        return {}
        
    try:
        w = wmi.WMI()
        for os in w.Win32_OperatingSystem():
            return {
                'Versión de Windows': f"{os.Caption} {os.Version}"
            }
    except Exception as e:
        print(f"Error obteniendo info SO detallada: {e}")
        return {}
    
class SystemMonitorPanel(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg="#2a2a2a", width=400)
        self.pack_propagate(False)  # Para que respete el tamaño asignado

        self.w = wmi.WMI(namespace="root\\wmi")

        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.ax_cpu = self.figure.add_subplot(211)
        self.ax_gpu = self.figure.add_subplot(212)

        self.ax_cpu.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax_gpu.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        self.x_data = [datetime.now() - timedelta(seconds=i) for i in reversed(range(60))]
        self.cpu_usage_data = [0] * 60
        self.cpu_temp_data = [0] * 60
        self.gpu_usage_data = [0] * 60
        self.gpu_temp_data = [0] * 60

        self.line_cpu_usage, = self.ax_cpu.plot(self.x_data, self.cpu_usage_data, label='Uso CPU (%)', color='cyan')
        self.line_cpu_temp, = self.ax_cpu.plot(self.x_data, self.cpu_temp_data, label='Temp CPU (°C)', color='orange')
        self.line_gpu_usage, = self.ax_gpu.plot(self.x_data, self.gpu_usage_data, label='Uso GPU (%)', color='green')
        self.line_gpu_temp, = self.ax_gpu.plot(self.x_data, self.gpu_temp_data, label='Temp GPU (°C)', color='red')

        self.ax_cpu.set_ylim(0, 100)
        self.ax_cpu.set_title("CPU")
        self.ax_cpu.legend(loc='upper left')

        self.ax_gpu.set_ylim(0, 100)
        self.ax_gpu.set_title("GPU")
        self.ax_gpu.legend(loc='upper left')

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        self.update_graphs()

    # Esta función la puedes poner como método privado dentro de la clase:
    def _get_cpu_temperature(self):
        try:
            temps = self.w.MSAcpi_ThermalZoneTemperature()
            if temps:
                return (temps[0].CurrentTemperature / 10) - 273.15
        except Exception as e:
            print(f"Error obteniendo temperatura CPU: {e}")
        return None

    
    def update_graphs(self):
        current_time = datetime.now()
        cpu_usage = psutil.cpu_percent()

        # Usar WMI en lugar de psutil
        cpu_temp = self._get_cpu_temperature()

        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            gpu_usage = gpu.load * 100
            gpu_temp = gpu.temperature
        else:
            gpu_usage = 0
            gpu_temp = 0

        self.x_data.append(current_time)
        self.cpu_usage_data.append(cpu_usage)
        self.cpu_temp_data.append(cpu_temp)
        self.gpu_usage_data.append(gpu_usage)
        self.gpu_temp_data.append(gpu_temp)

        self.x_data = self.x_data[-60:]
        self.cpu_usage_data = self.cpu_usage_data[-60:]
        self.cpu_temp_data = self.cpu_temp_data[-60:]
        self.gpu_usage_data = self.gpu_usage_data[-60:]
        self.gpu_temp_data = self.gpu_temp_data[-60:]

        self.line_cpu_usage.set_data(self.x_data, self.cpu_usage_data)
        self.line_cpu_temp.set_data(self.x_data, self.cpu_temp_data)
        self.line_gpu_usage.set_data(self.x_data, self.gpu_usage_data)
        self.line_gpu_temp.set_data(self.x_data, self.gpu_temp_data)

        self.ax_cpu.set_xlim(self.x_data[0], self.x_data[-1])
        self.ax_gpu.set_xlim(self.x_data[0], self.x_data[-1])

        self.canvas.draw()

        self.after(1000, self.update_graphs)

class SystemInfoApp:
    def __init__(self):
        self._data_requested = False   # <- inicializamos la bandera aquí
        self.ventana = tk.Tk()
        self.ventana.title("Información del sistema")
        self.ventana.configure(bg="#1e1e1e")
        self.ventana.geometry("720x1080")
        
        # Registrar limpieza al cerrar ventana
        self.ventana.protocol("WM_DELETE_WINDOW", self.on_closing)
        system_manager.register_cleanup()
        
        self.setup_ui()
        self.resultado_queue = Queue()
        self.cargar_datos()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        titulo = tk.Label(self.ventana, text="Especificaciones del sistema", 
                         font=("Arial", 16, "bold"), bg="#1e1e1e", fg="#00ffcc")
        titulo.pack(side="top", pady=10)
        
        # Frame de estado de carga
        self.frame_estado = tk.Frame(self.ventana, bg="#1e1e1e")
        self.frame_estado.pack(pady=10)
        
        self.label_estado = tk.Label(self.frame_estado, text="Cargando información del sistema...", 
                                    font=("Arial", 10), bg="#1e1e1e", fg="#ffaa00")
        self.label_estado.pack()
        
        # Contenedor principal
        panel_contenedor = tk.Frame(self.ventana, bg="#1e1e1e")
        panel_contenedor.pack(expand=True, fill="both")
        
        # Paneles
        self.panel_izquierdo = tk.Frame(panel_contenedor, bg="#2a2a2a", width=100)
        self.panel_izquierdo.pack(side="left", fill="y")
        
        # self.panel_derecho = tk.Frame(panel_contenedor, bg="#2a2a2a", width=100)
        # self.panel_derecho.pack(side="right", fill="y")
        
        self.panel_central = tk.Frame(panel_contenedor, bg="#1e1e1e")
        self.panel_central.pack(side="left", expand=True, fill="both")

        # Panel derecho: el monitor con gráficos
        self.panel_derecho = SystemMonitorPanel(panel_contenedor)
        self.panel_derecho.pack(side="right", fill="both", expand=True)
    
    def cargar_datos(self):
        """Inicia la carga de datos en hilos separados"""
        if self._data_requested:
            return
        self._data_requested = True

        # Definir las tareas con sus funciones y nombres
        tareas = [
            ('basica', obtener_info_basica),
            ('procesador', obtener_info_procesador),
            ('cpu_extra', obtener_datos_cpu_extra),
            ('cpuz', obtener_datos_cpuz),
            ('memoria', obtener_info_memoria),
            ('gpu', obtener_info_gpu),
            ('almacenamiento', obtener_info_almacenamiento),
            ('placa_base', obtener_info_placa_base),
            ('so_detallada', obtener_info_so_detallada)
        ]
        
        # Enviar todas las tareas a hilos
        futures = {}
        for nombre, funcion in tareas:
            future = system_manager.submit_task(funcion)
            if future:
                futures[nombre] = future
        
        # Monitorear resultados en un hilo separado
        monitor_thread = threading.Thread(
            target=self.monitorear_resultados, 
            args=(futures,),
            name="ResultMonitor",
            daemon=True
        )
        monitor_thread.start()
    
    def monitorear_resultados(self, futures):
        """Monitorea los resultados de las tareas en background"""
        if system_manager.shutdown_event.is_set():
            return
        resultados = {}
        completadas = 0
        total = len(futures)
        
        try:
            # Usar as_completed con timeout más corto y verificación de cierre
            timeout_per_batch = 30  # 30 segundos total para todas las tareas
            start_time = time.time()
            
            for future in as_completed(futures.values(), timeout=timeout_per_batch):
                # Verificar si debemos cerrar
                if system_manager.shutdown_event.is_set():
                    print("Cerrando monitor de resultados...")
                    break
                
                # Verificar timeout general
                if time.time() - start_time > timeout_per_batch:
                    print("Timeout general alcanzado")
                    break
                
                # Encontrar qué tarea completó
                nombre_tarea = None
                for nombre, fut in futures.items():
                    if fut == future:
                        nombre_tarea = nombre
                        break
                
                try:
                    resultado = future.result(timeout=5)  # Timeout individual
                    resultados[nombre_tarea] = resultado
                    completadas += 1
                    
                    # Actualizar estado en el hilo principal (solo si no cerrando)
                    if not system_manager.shutdown_event.is_set():
                        try:
                            self.ventana.after(0, self.actualizar_estado, completadas, total)
                        except:
                            break  # Ventana ya cerrada
                    
                except Exception as e:
                    print(f"Error en tarea {nombre_tarea}: {e}")
                    resultados[nombre_tarea] = {f'Error {nombre_tarea}': str(e)}
                    completadas += 1
            
            # Solo mostrar resultados si no estamos cerrando
            if not system_manager.shutdown_event.is_set():
                try:
                    self.ventana.after(0, self.mostrar_resultados, resultados)
                except:
                    print("No se pudieron mostrar resultados - ventana cerrada")
            
        except Exception as e:
            print(f"Error monitoreando resultados: {e}")
            if not system_manager.shutdown_event.is_set():
                try:
                    self.ventana.after(0, self.mostrar_error, f"Error cargando datos: {e}")
                except:
                    print("No se pudo mostrar error - ventana cerrada")
    
    def actualizar_estado(self, completadas, total):
        """Actualiza el estado de carga en la UI"""
        porcentaje = int((completadas / total) * 100)
        self.label_estado.config(text=f"Cargando... {completadas}/{total} ({porcentaje}%)")
    
    def mostrar_error(self, mensaje):
        """Muestra un error en la UI"""
        self.label_estado.config(text=f"Error: {mensaje}", fg="#ff4444")
    
    def mostrar_resultados(self, resultados):
        """Muestra los resultados finales en la UI"""
        try:
            # Ocultar estado de carga
            self.frame_estado.pack_forget()
            
            # Construir información completa
            info_completa = self.construir_info_completa(resultados)
            
            # Mostrar información
            self.mostrar_info_en_paneles(info_completa)

            # Mostrar mensaje de éxito
            messagebox.showinfo("Datos cargados", "Los datos fueron cargados correctamente ✅.")
            
        except Exception as e:
            print(f"Error mostrando resultados: {e}")
            self.mostrar_error(f"Error mostrando resultados: {e}")
    
    def construir_info_completa(self, resultados):
        """Construye la información completa combinando todos los resultados"""
        info = {}
        
        # Información básica
        if 'basica' in resultados:
            info.update(resultados['basica'])
        
        # Sistema operativo detallado
        if 'so_detallada' in resultados and resultados['so_detallada']:
            if 'Sistema Operativo' not in info:
                info['Sistema Operativo'] = {}
            info['Sistema Operativo'].update(resultados['so_detallada'])
        
        # Procesador (combinando todas las fuentes)
        info_proc = {}
        if 'cpuz' in resultados:
            info_proc.update(resultados['cpuz'])
        if 'procesador' in resultados:
            info_proc.update(resultados['procesador'])
        if 'cpu_extra' in resultados and resultados['cpu_extra']:
            info_proc.update(resultados['cpu_extra'])
        if info_proc:
            info['Procesador'] = info_proc
        
        # Memoria
        if 'memoria' in resultados:
            info['Memoria RAM'] = resultados['memoria']

        # GPU
        if 'gpu' in resultados:
            info['Tarjeta Gráfica'] = resultados['gpu']
        
        # Almacenamiento
        if 'almacenamiento' in resultados:
            info['Almacenamiento'] = resultados['almacenamiento']
        
        # Placa base
        if 'placa_base' in resultados:
            info['Placa Base'] = resultados['placa_base']
        
        return info
    
    def mostrar_info_en_paneles(self, info):
        """Muestra la información en los paneles correspondientes"""
        for seccion, datos in info.items():
            if not datos:  # Saltar secciones vacías
                continue
                
            if seccion == "Procesador":
                # Mostrar procesador en panel izquierdo
                self.agregar_seccion(self.panel_izquierdo, seccion, datos, "#2a2a2a")
            elif seccion == "Tarjeta Gráfica":
                # Mostrar procesador en panel izquierdo
                self.agregar_seccion(self.panel_izquierdo, seccion, datos, "#2a2a2a")
            else:
                # Resto de secciones en panel central
                self.agregar_seccion(self.panel_central, seccion, datos, "#1e1e1e")
    
    def agregar_seccion(self, panel, titulo, datos, bg_color):
        """Agrega una sección de información a un panel"""
        seccion_label = tk.Label(panel, text=f"--- {titulo} ---", anchor="w",
                                font=("Arial", 12, "bold"), bg=bg_color, fg="#00ffcc")
        seccion_label.pack(fill="x", padx=10, pady=(10, 2))
        
        for clave, valor in datos.items():
            wrap_length = 250 if panel == self.panel_izquierdo else 700
            label = tk.Label(panel, text=f"{clave}: {valor}", anchor="w",
                           bg=bg_color, fg="white", wraplength=wrap_length, justify="left")
            label.pack(fill="x", padx=20, pady=1)
    
    def on_closing(self):
        """Maneja el cierre de la aplicación de forma segura"""
        print("Cerrando aplicación...")
        try:
            # Marcar que estamos cerrando
            system_manager.shutdown_event.set()
            
            # Limpiar recursos en background para no bloquear
            cleanup_thread = threading.Thread(
                target=system_manager.cleanup, 
                name="CleanupThread",
                daemon=True
            )
            cleanup_thread.start()
            
            # Dar tiempo limitado para limpieza
            cleanup_thread.join(timeout=2.0)
            
            # Forzar cierre de ventana
            self.ventana.quit()  # Sale del mainloop
            self.ventana.destroy()  # Destruye la ventana
            
        except Exception as e:
            print(f"Error durante cierre: {e}")
            # Forzar salida si hay problemas
            self.ventana.quit()
            self.ventana.destroy()
    
    
    def run(self):
        """Ejecuta la aplicación con control de timeout"""
        app_running = True
        
        def timeout_handler():
            """Handler para timeout de aplicación (emergencia)"""
            nonlocal app_running
            if app_running:
                print("Timeout de aplicación - forzando cierre")
                try:
                    self.ventana.quit()
                    self.ventana.destroy()
                except:
                    pass
                app_running = False
        
        # Timer de seguridad (opcional - solo para emergencias)
        # timeout_timer = threading.Timer(300.0, timeout_handler)  # 5 minutos
        # timeout_timer.daemon = True
        # timeout_timer.start()
        
        try:
            # Asegurar que la ventana esté visible antes de mainloop
            self.ventana.update_idletasks()
            self.ventana.deiconify()  # Asegurar que esté visible
            
            print("Iniciando mainloop...")
            logging.debug("Iniciando mainloop...")
            self.ventana.mainloop()
            print("Mainloop terminado")
            logging.debug("Mainloop terminado")
            
            
        except KeyboardInterrupt:
            print("Interrupción por teclado (Ctrl+C)")
        except Exception as e:
            print(f"Error en mainloop: {e}")
            try:
                messagebox.showerror("Error en la aplicación", str(e))
            except:
                print("No se pudo mostrar messagebox de error")
        finally:
            app_running = False
            # timeout_timer.cancel()  # Cancelar timer si estaba activo
            print("Limpieza final en run()")

def signal_handler(signum, frame):
    """Maneja señales del sistema para cierre limpio."""
    print(f"Señal recibida: {signum}")
    try:
        system_manager.cleanup()
    except Exception as e:
        print(f"Error durante la limpieza en signal_handler: {e}")
    # Forzar salida inmediata sin ejecutar funciones atexit
    os._exit(0)

def is_already_running():
        current_process = psutil.Process()
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            if proc.info['pid'] == current_process.pid:
                continue
            if proc.info['exe'] == current_process.exe():
                return True
        return False

def start_app():

    if is_already_running():
        print("La aplicación ya está ejecutándose")
        sys.exit(0)

    # Registrar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    app = None
    try:
        print("Iniciando aplicación...")
        try:
            run_matrix_effect()
        except subprocess.CalledProcessError as e:
            print(f"matrix_effect.exe terminó con error (probablemente cerrado con la X): {e}")
        except Exception as e:
            print(f"Error inesperado ejecutando matrix_effect.exe: {e}")
        finally:
            app = SystemInfoApp()
            app.run()
            print("Aplicación terminada normalmente")

    except KeyboardInterrupt:
        print("Aplicación interrumpida por usuario")

    except Exception as e:
        print(f"Error crítico: {e}")
        try:
            messagebox.showerror("Error crítico", str(e))
        except Exception as msgbox_err:
            print(f"No se pudo mostrar messagebox crítico: {msgbox_err}")

    finally:
        print("Ejecutando limpieza final...")
        try:
            if app and hasattr(app, 'ventana'):
                try:
                    app.ventana.quit()
                    app.ventana.destroy()
                except Exception as e:
                    print(f"Error al cerrar ventana: {e}")
            system_manager.cleanup()
        except Exception as cleanup_error:
            print(f"Error en limpieza final: {cleanup_error}")

        print("Aplicación completamente cerrada")

        # Forzar salida si sys.exit falla (por ejemplo, en algunos entornos)
        try:
            sys.exit(0)
        except SystemExit:
            pass
        except Exception:
            os._exit(0)

if __name__ == "__main__":
    start_app()
    