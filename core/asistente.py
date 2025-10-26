import requests
import json
import time
import threading
import multiprocessing
import speech_recognition as sr

from config.config_manager import ConfigManager
from core.gestor_modelos import GestorModelos
from herramientas.explorador_archivos import ExploradorArchivos


class AsistenteIA:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        self.gestor_modelos = GestorModelos()
        self.explorador_archivos = ExploradorArchivos()
        self.inicializar_estados()

        # CONTEXTO SIMPLIFICADO
        self.contexto_conversacion = {
            'ultima_ruta': 'usuario',
            'historial_reciente': []
        }
        # ✅ NUEVO: Profundidad por defecto
        self.profundidad_actual = 2

    def inicializar_estados(self):
        """Inicializa estados del sistema"""
        self.voz_proceso = None
        self.voz_activada = self.config["voz_activada"]
        self.microfono_activado = self.config["microfono_activado"]
        self.personalidad_actual = self.config["personalidad_actual"]
        self.config_voz = self.config["config_voz"]
        self.descarga_activa = False
        self.app_cerrando = False

    # ==================== SISTEMA SIMPLIFICADO ====================

    def _debe_usar_herramienta_archivos(self, mensaje_usuario):
        """SOLO determina DÓNDE buscar la información del sistema (no SI debe buscar)"""

        # PROMPT MODIFICADO - Solo para determinar la ubicación
        prompt_decision = f"""
    Eres un asistente que determina DÓNDE buscar en el sistema de archivos según lo que pide el usuario.

    MENSAJE DEL USUARIO: {mensaje_usuario}

    ANALIZA el mensaje y DETERMINA la ubicación más apropiada donde buscar:

    - "escritorio" si menciona escritorio o desktop
    - "documentos" si menciona documentos, documents
    - "descargas" si menciona descargas, downloads  
    - "imágenes" si menciona imágenes, pictures, fotos
    - "música" si menciona música, music
    - "vídeos" si menciona vídeos, videos
    - "actual" si menciona carpeta actual, directorio actual
    - "proyecto" si menciona proyecto, project
    - "ordenador" si menciona ordenador, sistema, o dispositivo
    - "usuario" si menciona al usuario, a sí mismo, algo de su propiedad, o si no especifica donde buscar

    RESPONDE SOLO con la ubicación (una palabra)

    Ejemplos:
    - "¿Cuántos archivos tengo?" → "usuario"
    - "¿Qué hay en documentos?" → "documentos" 
    - "Buscar archivos en descargas" → "descargas"
    - "Explorar mi sistema" → "ordenador"

    RESPUESTA:
    """

        print(f"🔍 Consultando a la IA dónde buscar información del sistema...")

        try:
            resp = requests.post(
                self.config["ollama_url"],
                json={
                    "model": self.config["ollama_model"],
                    "prompt": prompt_decision,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 20,
                        "top_k": 10,
                        "top_p": 0.9
                    }
                },
                timeout=10
            )

            if resp.status_code == 200:
                ubicacion = resp.json().get("response", "").strip().lower()
                print(f"🎯 IA indica buscar en: {ubicacion}")

                # Validar y normalizar la ubicación
                ubicaciones_validas = ['escritorio', 'documentos', 'descargas', 'imágenes', 'música', 'vídeos',
                                       'actual', 'proyecto', 'ordenador', 'usuario']

                if ubicacion in ubicaciones_validas:
                    self.contexto_conversacion['ultima_ruta'] = ubicacion
                    return ubicacion
                else:
                    # Fallback a ubicación por defecto
                    print(f"⚠️ Ubicación no válida '{ubicacion}', usando 'usuario' por defecto")
                    self.contexto_conversacion['ultima_ruta'] = 'usuario'
                    return 'usuario'

        except Exception as e:
            print(f"⚠️ Error consultando a la IA: {e}")

        # Fallback - determinar ubicación basada en palabras clave
        return self._determinar_ubicacion_fallback(mensaje_usuario)

    def _determinar_ubicacion_fallback(self, mensaje_usuario):
        """Determina la ubicación basada en palabras clave cuando falla la IA"""
        mensaje = mensaje_usuario.lower()

        ubicaciones = {
            'escritorio': ['escritorio', 'desktop'],
            'documentos': ['documentos', 'documents', 'documento'],
            'descargas': ['descargas', 'downloads', 'descargar'],
            'imágenes': ['imágenes', 'imagenes', 'fotos', 'pictures', 'photos'],
            'música': ['música', 'musica', 'music', 'canciones'],
            'vídeos': ['vídeos', 'videos', 'video', 'películas'],
            'actual': ['actual', 'current', 'directorio actual', 'carpeta actual'],
            'proyecto': ['proyecto', 'project']
        }

        for ubicacion, palabras in ubicaciones.items():
            for palabra in palabras:
                if palabra in mensaje:
                    print(f"📍 Fallback: detectada ubicación '{ubicacion}' por palabra '{palabra}'")
                    self.contexto_conversacion['ultima_ruta'] = ubicacion
                    return ubicacion

        # Por defecto
        print("📍 Fallback: usando ubicación por defecto 'usuario'")
        self.contexto_conversacion['ultima_ruta'] = 'usuario'
        return 'usuario'

    def _obtener_ruta_inteligente(self, mensaje_usuario):
        """Obtiene la ruta del contexto (ya decidida por la IA)"""
        ruta = self.contexto_conversacion['ultima_ruta']
        print(f"📍 Usando ruta del contexto IA: {ruta}")
        return ruta

    def _ejecutar_explorador_completo(self, mensaje_usuario, profundidad=2):
        """Ejecuta el explorador para obtener información COMPLETA del sistema"""
        ruta = self._obtener_ruta_inteligente(mensaje_usuario)

        print(f"🔍 Ejecutando explorador COMPLETO:")
        print(f"   - Ruta: {ruta}")
        print(f"   - Profundidad: {profundidad}")
        print(f"   - Mensaje original: '{mensaje_usuario}'")

        # ✅ CORREGIDO: Pasar la profundidad al explorador
        resultado = self.explorador_archivos.obtener_estructura_carpetas(
            ruta,
            None,  # Sin término de búsqueda específico
            profundidad  # ← ¡PASAR LA PROFUNDIDAD!
        )
        print(f"📊 Información del sistema obtenida ({len(resultado)} caracteres)")
        return resultado

    # ==================== SISTEMA PRINCIPAL MEJORADO ====================

    def generar_respuesta_ollama(self, mensaje_usuario, forzar_explorador=False, profundidad=2):
        """Genera respuesta - Puede forzar el uso del explorador mediante el botón"""
        if self.app_cerrando:
            return "❌ Aplicación cerrándose..."

        modelo_actual = self.config["ollama_model"]

        if not self.gestor_modelos.verificar_modelo_instalado(modelo_actual):
            return f"❌ {modelo_actual} no instalado. Usa el botón 'Descargar Modelo'."

        # DECISIÓN MODIFICADA: Solo usar explorador si se fuerza manualmente
        usar_herramienta = forzar_explorador

        contexto_herramienta = ""
        if usar_herramienta:
            print("🛠️ Obteniendo información COMPLETA del sistema (activación manual)...")

            # Primero determinar DÓNDE buscar
            ubicacion = self._debe_usar_herramienta_archivos(mensaje_usuario)
            print(f"📍 Buscando en: {ubicacion}")

            # ✅ CORREGIDO: Pasar la profundidad al ejecutar el explorador
            resultado_herramienta = self._ejecutar_explorador_completo(mensaje_usuario, profundidad)

            contexto_herramienta = f"""

    INFORMACIÓN COMPLETA DEL SISTEMA DE ARCHIVOS (Ubicación: {ubicacion}, Profundidad: {profundidad} niveles):
    {resultado_herramienta}

    BASÁNDOTE en esta información completa del sistema, analiza y responde a la pregunta del usuario.
    La información incluye estadísticas, ejemplos de archivos/carpetas, y cualquier coincidencia relevante.
    """

        # PREPARAR PROMPT FINAL (igual que antes)
        personalidades = self.config_manager.obtener_personalidades()
        timeout = self.config_manager.obtener_modelos_compatibles().get(modelo_actual, {}).get("timeout", 300)

        prompt = f"""
    {personalidades[self.personalidad_actual]['prompt']}
    {contexto_herramienta}

    PREGUNTA DEL USUARIO: {mensaje_usuario}

    INSTRUCCIONES:
    1. Si hay información del sistema arriba, ANALÍZALA COMPLETAMENTE y responde basándote en ella
    2. Si no hay información del sistema, responde normalmente
    3. Para preguntas sobre archivos/carpetas, USA los datos específicos de la información del sistema
    4. Sé preciso con números y nombres cuando uses la información del sistema

    RESPUESTA:
    """

        print(f"🧠 Enviando a {modelo_actual}...")
        print(f"📝 Información del sistema: {'SÍ (manual)' if usar_herramienta else 'NO'}")

        try:
            start_time = time.time()

            resp = requests.post(
                self.config["ollama_url"],
                json={
                    "model": modelo_actual,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 2048,
                        "top_k": 40,
                        "top_p": 0.9
                    }
                },
                timeout=timeout
            )

            elapsed_time = time.time() - start_time

            if resp.status_code == 200:
                data = resp.json()
                respuesta = data.get("response", "").strip()

                if respuesta:
                    print(f"✅ Respuesta en {elapsed_time:.1f}s")
                    # Añadir indicador contextual
                    if usar_herramienta:
                        respuesta = f"🔍 (Analizando sistema de archivos - Ubicación: {self.contexto_conversacion['ultima_ruta']}, Profundidad: {profundidad} niveles)\n{respuesta}"
                    return respuesta
                else:
                    return "❌ Respuesta vacía"

            else:
                return f"❌ Error HTTP {resp.status_code}"

        except requests.exceptions.Timeout:
            return f"⏰ TIMEOUT: El modelo está pensando..."
        except requests.exceptions.ConnectionError:
            return "🔌 Error: Ollama no está corriendo."
        except Exception as e:
            return f"❌ Error: {str(e)}"

    # ✅ CORREGIDO: Método actualizado para aceptar profundidad
    def activar_explorador_archivos(self, mensaje_usuario, profundidad=2):
        """Activa manualmente el explorador de archivos para la consulta actual"""
        print(f"🔧 Activación manual del explorador de archivos - Profundidad: {profundidad}")

        # Guardar la profundidad actual
        self.profundidad_actual = profundidad

        # Determinar dónde buscar
        ubicacion = self._debe_usar_herramienta_archivos(mensaje_usuario)

        # Generar respuesta forzando el explorador CON PROFUNDIDAD
        return self.generar_respuesta_ollama(mensaje_usuario, forzar_explorador=True, profundidad=profundidad)

    # ==================== MÉTODOS EXISTENTES (MANTENIDOS) ====================

    def cambiar_modelo(self, nuevo_modelo, callback_progreso=None):
        """Cambia el modelo actual"""
        if self.app_cerrando:
            return "❌ Aplicación cerrándose...", "error"

        modelos_compatibles = self.config_manager.obtener_modelos_compatibles()
        if nuevo_modelo not in modelos_compatibles:
            return f"❌ Modelo no compatible", "error"

        # Verificar si ya está instalado
        if self.gestor_modelos.verificar_modelo_instalado(nuevo_modelo):
            self.config["ollama_model"] = nuevo_modelo
            self.config_manager.guardar_configuracion()
            velocidad = modelos_compatibles[nuevo_modelo]["timeout"]
            return f"✅ Cambiado a {nuevo_modelo} (⏱️ {velocidad}s)", "success"

        # Iniciar descarga
        self.descarga_activa = True

        def on_progreso(mensaje, tipo):
            if callback_progreso:
                callback_progreso(mensaje, tipo)

        hilo_descarga = self.gestor_modelos.descargar_modelo(nuevo_modelo, on_progreso)

        def watcher_descarga():
            hilo_descarga.join(timeout=300)
            self.descarga_activa = False
            self.gestor_modelos.actualizar_modelos_instalados()

            if self.gestor_modelos.verificar_modelo_instalado(nuevo_modelo):
                self.config["ollama_model"] = nuevo_modelo
                self.config_manager.guardar_configuracion()
                if callback_progreso:
                    callback_progreso(f"🎉 {nuevo_modelo} listo!", "success")

        threading.Thread(target=watcher_descarga, daemon=True).start()

        return f"📥 Descargando {nuevo_modelo}...", "download"

    def tts_process(self, texto, config_voz):
        """Proceso de texto a voz"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', config_voz["velocidad"])
            engine.setProperty('volume', config_voz["volumen"])
            engine.say(texto)
            engine.runAndWait()
        except Exception as e:
            print(f"🔊 Error en voz: {e}")

    def silenciar_voz_actual(self):
        """Silencia voz actual"""
        if self.voz_proceso and self.voz_proceso.is_alive():
            try:
                self.voz_proceso.terminate()
                self.voz_proceso.join(timeout=1.0)
            except:
                pass

    def toggle_voz(self):
        """Activa/desactiva voz"""
        self.voz_activada = not self.voz_activada
        self.config["voz_activada"] = self.voz_activada
        if not self.voz_activada:
            self.silenciar_voz_actual()
        estado = "activada" if self.voz_activada else "desactivada"
        return self.voz_activada, f"🔊 Voz {estado}"

    def toggle_microfono(self):
        """Activa/desactiva micrófono"""
        self.microfono_activado = not self.microfono_activado
        self.config["microfono_activado"] = self.microfono_activado
        estado = "activado" if self.microfono_activado else "desactivado"
        return self.microfono_activado, f"🎤 Mic {estado}"

    def verificar_modelo_instalado(self, nombre_modelo):
        """Verifica si un modelo está instalado"""
        return self.gestor_modelos.verificar_modelo_instalado(nombre_modelo)

    def obtener_modelos_compatibles(self):
        """Devuelve modelos compatibles"""
        return self.config_manager.obtener_modelos_compatibles()

    def obtener_personalidades(self):
        """Devuelve personalidades disponibles"""
        return self.config_manager.obtener_personalidades()