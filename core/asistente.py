import requests
import json
import time
import threading
import multiprocessing
import speech_recognition as sr
import re  # ✅ NUEVO: Para extraer términos de búsqueda

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

    # ✅ NUEVO: Método para extraer términos de búsqueda
    def _extraer_termino_busqueda(self, mensaje):
        """Extrae términos de búsqueda específicos del mensaje del usuario"""
        mensaje_lower = mensaje.lower().strip()

        print(f"🔍 Analizando mensaje para extraer búsqueda: '{mensaje}'")

        # Patrones de búsqueda comunes
        patrones = [
            r'carpeta que se llame\s+["\']?([^"\'\?]+)["\']?',
            r'archivo que se llame\s+["\']?([^"\'\?]+)["\']?',
            r'buscar\s+["\']?([^"\'\?]+)["\']?',
            r'[\'"]([^\'"]+)[\'"]',  # Texto entre comillas
            r'que se llama\s+([^\?\.,!]+)',  # "que se llama X"
            r'llamad[ao]\s+([^\?\.,!]+)',  # "llamada X" o "llamado X"
        ]

        for patron in patrones:
            match = re.search(patron, mensaje_lower)
            if match:
                termino = match.group(1).strip()
                if termino and len(termino) > 1:  # Evitar términos muy cortos
                    print(f"🎯 Término de búsqueda extraído: '{termino}'")
                    return termino

        # Fallback: buscar palabras después de "llame" o "llama"
        palabras_clave = ["llame", "llama", "llamada", "llamado", "buscar", "encuentra"]
        palabras = mensaje_lower.split()

        for i, palabra in enumerate(palabras):
            if palabra in palabras_clave and i + 1 < len(palabras):
                termino = palabras[i + 1].strip('?.,!\"\'')
                if termino and len(termino) > 1:
                    print(f"🎯 Término de búsqueda (fallback): '{termino}'")
                    return termino

        print("🔍 No se extrajo término de búsqueda específico")
        return None

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
        """Genera respuesta con búsqueda INTELIGENTE"""
        if self.app_cerrando:
            return "❌ Aplicación cerrándose..."

        modelo_actual = self.config["ollama_model"]

        if not self.gestor_modelos.verificar_modelo_instalado(modelo_actual):
            return f"❌ {modelo_actual} no instalado. Usa el botón 'Descargar Modelo'."

        # DECISIÓN: Solo usar explorador si se fuerza manualmente
        usar_herramienta = forzar_explorador

        contexto_herramienta = ""
        termino_busqueda = None

        if usar_herramienta:
            print("🛠️ Obteniendo información del sistema (activación manual)...")

            # ✅ PRIMERO: Extraer término de búsqueda si existe
            termino_busqueda = self._extraer_termino_busqueda(mensaje_usuario)

            # Determinar DÓNDE buscar
            ubicacion = self._debe_usar_herramienta_archivos(mensaje_usuario)
            print(f"📍 Buscando en: {ubicacion}")

            # ✅ DECIDIR: ¿Búsqueda específica o exploración completa?
            if termino_busqueda:
                print(f"🎯 EJECUTANDO BÚSQUEDA ESPECÍFICA: '{termino_busqueda}'")
                ruta = self._obtener_ruta_inteligente(mensaje_usuario)
                resultado_herramienta = self.explorador_archivos.obtener_estructura_carpetas(
                    ruta, termino_busqueda, profundidad
                )
                tipo_busqueda = "BÚSQUEDA ESPECÍFICA"
            else:
                print("📊 EJECUTANDO EXPLORACIÓN COMPLETA")
                resultado_herramienta = self._ejecutar_explorador_completo(mensaje_usuario, profundidad)
                tipo_busqueda = "EXPLORACIÓN COMPLETA"

            contexto_herramienta = f"""

INFORMACIÓN DEL SISTEMA ({tipo_busqueda}):
Ubicación: {ubicacion}
Profundidad: {profundidad} niveles
{termino_busqueda and f"Término buscado: '{termino_busqueda}'" or ""}

RESULTADO:
{resultado_herramienta}

INSTRUCCIONES ESPECÍFICAS:
1. Analiza METICULOSAMENTE la información proporcionada
2. Responde DIRECTAMENTE a la pregunta del usuario
3. Si hay resultados de búsqueda, menciónalos EXPLÍCITAMENTE
4. Si no hay resultados, indica claramente "No se encontró"
5. Sé PRECISO con nombres y ubicaciones

PREGUNTA DEL USUARIO: {mensaje_usuario}

RESPUESTA BASADA EN LOS DATOS:
"""

        # PREPARAR PROMPT FINAL
        personalidades = self.config_manager.obtener_personalidades()
        timeout = self.config_manager.obtener_modelos_compatibles().get(modelo_actual, {}).get("timeout", 300)

        prompt = f"""
{personalidades[self.personalidad_actual]['prompt']}
{contexto_herramienta}

PREGUNTA DEL USUARIO: {mensaje_usuario}

RESPUESTA:
"""

        print(f"🧠 Enviando a {modelo_actual}...")
        print(
            f"📝 Información del sistema: {'SÍ (búsqueda)' if termino_busqueda else 'SÍ (completa)' if usar_herramienta else 'NO'}")

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
                        if termino_busqueda:
                            respuesta = f"🔍 (Búsqueda: '{termino_busqueda}' en {ubicacion}, Profundidad: {profundidad})\n{respuesta}"
                        else:
                            respuesta = f"🔍 (Explorando: {ubicacion}, Profundidad: {profundidad})\n{respuesta}"
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

    # ✅ MANTENER los métodos existentes
    def activar_explorador_archivos(self, mensaje_usuario, profundidad=2):
        """Activa manualmente el explorador de archivos"""
        print(f"🔧 Activación manual del explorador - Profundidad: {profundidad}")
        self.profundidad_actual = profundidad
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