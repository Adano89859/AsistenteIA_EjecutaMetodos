import requests
import subprocess
import threading
import time


class GestorModelos:
    """Gestiona modelos de Ollama optimizado para velocidad"""

    def __init__(self):
        self.modelos_instalados = self.obtener_modelos_instalados()
        self.descarga_activa = False

    def obtener_modelos_instalados(self):
        """Obtiene lista de modelos instalados"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                modelos_data = response.json().get('models', [])
                return [modelo.get('name', '') for modelo in modelos_data]
            return []
        except:
            return []

    def verificar_modelo_instalado(self, nombre_modelo):
        """Verifica si un modelo está instalado"""
        return nombre_modelo in self.modelos_instalados

    def actualizar_modelos_instalados(self):
        """Actualiza la lista de modelos instalados"""
        self.modelos_instalados = self.obtener_modelos_instalados()

    def descargar_modelo(self, nombre_modelo, callback_progreso=None):
        """Descarga modelo mostrando progreso"""

        def descargar():
            try:
                if callback_progreso:
                    callback_progreso(f"⏬ Descargando {nombre_modelo}...", "download")

                proceso = subprocess.Popen(
                    ['ollama', 'pull', nombre_modelo],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    encoding='utf-8'
                )

                for linea in proceso.stdout:
                    if linea.strip():
                        if callback_progreso:
                            callback_progreso(f"📥 {linea.strip()}", "download")

                proceso.wait()

                if proceso.returncode == 0:
                    if callback_progreso:
                        callback_progreso(f"✅ {nombre_modelo} listo!", "success")
                    return True
                else:
                    if callback_progreso:
                        callback_progreso(f"❌ Error en descarga", "error")
                    return False

            except Exception as e:
                if callback_progreso:
                    callback_progreso(f"💥 Error: {str(e)}", "error")
                return False

        hilo = threading.Thread(target=descargar)
        hilo.daemon = True
        hilo.start()
        return hilo