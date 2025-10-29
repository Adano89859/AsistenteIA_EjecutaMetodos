import requests
import json
import time
import threading
import multiprocessing
import speech_recognition as sr
import re

from config.config_manager import ConfigManager
from core.gestor_modelos import GestorModelos
from herramientas.explorador_archivos import ExploradorArchivos
from herramientas.rendimiento_sistema import MonitorRendimiento  # ✅ NUEVO IMPORT


class AsistenteIA:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        self.gestor_modelos = GestorModelos()
        self.explorador_archivos = ExploradorArchivos()
        self.monitor_rendimiento = MonitorRendimiento()  # ✅ NUEVA INSTANCIA
        self.inicializar_estados()

        # CONTEXTO SIMPLIFICADO
        self.contexto_conversacion = {
            'ultima_ruta': 'usuario',
            'historial_reciente': [],
            'ubicacion_manual': None
        }
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

    # ✅ MODIFICADO: Método principal para modo rendimiento (ahora usa módulo separado)
    def obtener_rendimiento_sistema(self, mensaje_usuario):
        """Obtiene métricas del sistema y las integra en la respuesta de la IA"""
        print("📊 Modo Rendimiento - Obteniendo métricas del sistema...")

        # ✅ USAR MÓDULO SEPARADO para obtener métricas
        metricas = self.monitor_rendimiento.obtener_metricas_completas()

        # Generar respuesta contextualizada con la IA
        return self.generar_respuesta_ollama_con_metricas(mensaje_usuario, metricas)

    # ✅ MÉTODO ACTUALIZADO: Para generar respuesta con métricas MEJORADO
    def generar_respuesta_ollama_con_metricas(self, mensaje_usuario, metricas):
        """Genera respuesta integrando métricas del sistema en el contexto"""

        # Construir contexto de métricas MEJORADO con información adicional
        contexto_metricas = f"""
📊 **INFORMACIÓN DE RENDIMIENTO DEL SISTEMA (TIEMPO REAL):**

• 🖥️ **CPU:** {metricas['cpu']} de uso
• 🧠 **Memoria RAM:** {metricas['memoria']}
• 🔄 **Procesos activos:** {metricas['procesos']}
• 💾 **Disco:** {metricas['disco']}
• 🌡️ **Temperatura:** {metricas['temperatura']}
• ⏰ **Tiempo de actividad:** {metricas['tiempo_actividad']}
• 📡 **Red:** {metricas['red']}
• 💻 **Sistema:** {metricas['info_sistema'].get('sistema', 'Desconocido')} - {metricas['info_sistema'].get('arquitectura', '?')}
• 🔢 **Núcleos:** {metricas['info_sistema'].get('nucleos_fisicos', '?')} físicos, {metricas['info_sistema'].get('nucleos_logicos', '?')} lógicos
{'• 🔥 **Procesos destacados:** ' + ', '.join(metricas['procesos_top']) if metricas['procesos_top'] and metricas['procesos_top'][0] not in ['Error', 'Sin procesos destacados'] else ''}

**INSTRUCCIONES PARA LA IA:**
1. Analiza estas métricas de rendimiento en tiempo real
2. Responde la pregunta del usuario contextualizando con estos datos
3. Si hay valores altos (CPU >80%, Memoria >85%, Disco >90%), sugiere optimizaciones
4. Explica el significado de las métricas relevantes para la pregunta
5. Si la temperatura no está disponible, explica que es normal en algunos sistemas y no indica problemas
6. Considera la información del sistema ({metricas['info_sistema'].get('sistema', 'Desconocido')}) en tu análisis
7. Sé conciso pero informativo sobre el estado del sistema

PREGUNTA DEL USUARIO: {mensaje_usuario}

RESPUESTA BASADA EN LAS MÉTRICAS ACTUALES:
"""

        modelo_actual = self.config["ollama_model"]
        personalidades = self.config_manager.obtener_personalidades()
        timeout = self.config_manager.obtener_modelos_compatibles().get(modelo_actual, {}).get("timeout", 300)

        prompt_final = f"""
{personalidades[self.personalidad_actual]['prompt']}
{contexto_metricas}
"""

        print(f"🧠 Enviando a {modelo_actual} con métricas del sistema...")

        try:
            start_time = time.time()

            resp = requests.post(
                self.config["ollama_url"],
                json={
                    "model": modelo_actual,
                    "prompt": prompt_final,
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
                    print(f"✅ Respuesta con métricas en {elapsed_time:.1f}s")
                    # Añadir indicador contextual del modo rendimiento
                    respuesta = f"📊 (Modo Rendimiento - Métricas en tiempo real)\n{respuesta}"
                    return respuesta
                else:
                    return "❌ Respuesta vacía del modelo"

            else:
                return f"❌ Error HTTP {resp.status_code} al obtener respuesta con métricas"

        except requests.exceptions.Timeout:
            return f"⏰ TIMEOUT: El modelo está procesando las métricas del sistema..."
        except requests.exceptions.ConnectionError:
            return "🔌 Error: Ollama no está corriendo."
        except Exception as e:
            return f"❌ Error procesando métricas: {str(e)}"

    # ==================== MÉTODOS EXISTENTES (SE MANTIENEN IGUAL) ====================

    def establecer_ubicacion_manual(self, ubicacion):
        """Establece una ubicación manual para la búsqueda"""
        if ubicacion == "automático":
            self.contexto_conversacion['ubicacion_manual'] = None
            print("📍 Ubicación manual: Automático (IA decide)")
        else:
            self.contexto_conversacion['ubicacion_manual'] = ubicacion
            print(f"📍 Ubicación manual establecida: {ubicacion}")

    def _obtener_ubicacion_busqueda(self, mensaje_usuario):
        """Obtiene la ubicación para buscar (manual prevalece sobre automático)"""
        if self.contexto_conversacion.get('ubicacion_manual'):
            ubicacion_manual = self.contexto_conversacion['ubicacion_manual']
            print(f"📍 Usando ubicación MANUAL: {ubicacion_manual}")
            self.contexto_conversacion['ultima_ruta'] = ubicacion_manual
            return ubicacion_manual

        print("📍 Modo AUTOMÁTICO: Consultando a la IA...")
        return self._debe_usar_herramienta_archivos(mensaje_usuario)

    def _extraer_termino_busqueda(self, mensaje):
        """Extrae términos de búsqueda específicos del mensaje del usuario"""
        mensaje_lower = mensaje.lower().strip()
        print(f"🔍 Analizando mensaje para extraer búsqueda: '{mensaje}'")

        patrones = [
            r'carpeta que se llame\s+["\']?([^"\'\?]+)["\']?',
            r'archivo que se llame\s+["\']?([^"\'\?]+)["\']?',
            r'buscar\s+["\']?([^"\'\?]+)["\']?',
            r'[\'"]([^\'"]+)[\'"]',
            r'que se llama\s+([^\?\.,!]+)',
            r'llamad[ao]\s+([^\?\.,!]+)',
        ]

        for patron in patrones:
            match = re.search(patron, mensaje_lower)
            if match:
                termino = match.group(1).strip()
                if termino and len(termino) > 1:
                    print(f"🎯 Término de búsqueda extraído: '{termino}'")
                    return termino

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

    def _debe_usar_herramienta_archivos(self, mensaje_usuario):
        """SOLO determina DÓNDE buscar la información del sistema"""
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

                ubicaciones_validas = ['escritorio', 'documentos', 'descargas', 'imágenes', 'música', 'vídeos',
                                       'actual', 'proyecto', 'ordenador', 'usuario']

                if ubicacion in ubicaciones_validas:
                    self.contexto_conversacion['ultima_ruta'] = ubicacion
                    return ubicacion
                else:
                    print(f"⚠️ Ubicación no válida '{ubicacion}', usando 'usuario' por defecto")
                    self.contexto_conversacion['ultima_ruta'] = 'usuario'
                    return 'usuario'

        except Exception as e:
            print(f"⚠️ Error consultando a la IA: {e}")

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

        print("📍 Fallback: usando ubicación por defecto 'usuario'")
        self.contexto_conversacion['ultima_ruta'] = 'usuario'
        return 'usuario'

    def _obtener_ruta_inteligente(self, mensaje_usuario):
        """Obtiene la ruta del contexto (ya decidida por la IA o manual)"""
        ruta = self.contexto_conversacion['ultima_ruta']
        print(f"📍 Usando ruta del contexto: {ruta}")
        return ruta

    def _ejecutar_explorador_completo(self, mensaje_usuario, profundidad=2):
        """Ejecuta el explorador para obtener información COMPLETA del sistema"""
        ubicacion = self._obtener_ubicacion_busqueda(mensaje_usuario)

        print(f"🔍 Ejecutando explorador COMPLETO:")
        print(f"   - Ruta: {ubicacion}")
        print(f"   - Profundidad: {profundidad}")
        print(f"   - Mensaje original: '{mensaje_usuario}'")

        resultado = self.explorador_archivos.obtener_estructura_carpetas(
            ubicacion,
            None,
            profundidad
        )
        print(f"📊 Información del sistema obtenida ({len(resultado)} caracteres)")
        return resultado

    def generar_respuesta_ollama(self, mensaje_usuario, forzar_explorador=False, profundidad=2, ubicacion_manual=None):
        """Genera respuesta con búsqueda INTELIGENTE"""
        if self.app_cerrando:
            return "❌ Aplicación cerrándose..."

        if ubicacion_manual:
            self.establecer_ubicacion_manual(ubicacion_manual)

        modelo_actual = self.config["ollama_model"]

        if not self.gestor_modelos.verificar_modelo_instalado(modelo_actual):
            return f"❌ {modelo_actual} no instalado. Usa el botón 'Descargar Modelo'."

        usar_herramienta = forzar_explorador
        contexto_herramienta = ""
        termino_busqueda = None

        if usar_herramienta:
            print("🛠️ Obteniendo información del sistema (activación manual)...")

            termino_busqueda = self._extraer_termino_busqueda(mensaje_usuario)
            ubicacion_real = self._obtener_ubicacion_busqueda(mensaje_usuario)
            print(f"📍 Buscando en: {ubicacion_real}")

            if termino_busqueda:
                print(f"🎯 EJECUTANDO BÚSQUEDA ESPECÍFICA: '{termino_busqueda}'")
                resultado_herramienta = self.explorador_archivos.obtener_estructura_carpetas(
                    ubicacion_real, termino_busqueda, profundidad
                )
                tipo_busqueda = "BÚSQUEDA ESPECÍFICA"
            else:
                print("📊 EJECUTANDO EXPLORACIÓN COMPLETA")
                resultado_herramienta = self._ejecutar_explorador_completo(mensaje_usuario, profundidad)
                tipo_busqueda = "EXPLORACIÓN COMPLETA"

            contexto_herramienta = f"""

    INFORMACIÓN DEL SISTEMA ({tipo_busqueda}):

    📍 **UBICACIÓN REAL DE BÚSQUEDA:** {ubicacion_real}
    🔍 **Profundidad:** {profundidad} niveles
    {termino_busqueda and f"🎯 **Término buscado:** '{termino_busqueda}'" or ""}
    📋 **Modo:** {'MANUAL (usuario seleccionó esta ubicación)' if self.contexto_conversacion.get('ubicacion_manual') else 'AUTOMÁTICO (IA decidió esta ubicación)'}

    **IMPORTANTE:** La información siguiente es EXCLUSIVAMENTE de la ubicación '{ubicacion_real}'. 
    Responde basándote SOLO en esta ubicación, incluso si el usuario menciona otras.

    RESULTADO:
    {resultado_herramienta}

    INSTRUCCIONES ESPECÍFICAS:
    1. La búsqueda se realizó EXCLUSIVAMENTE en: {ubicacion_real}
    2. Responde refiriéndote SIEMPRE a esta ubicación real
    3. Si el usuario menciona otra ubicación, aclara que la información es de {ubicacion_real}
    4. Si hay resultados de búsqueda, menciónalos EXPLÍCITAMENTE en el contexto de {ubicacion_real}
    5. Si no hay resultados, indica claramente "No se encontró en {ubicacion_real}"

    PREGUNTA DEL USUARIO: {mensaje_usuario}

    RESPUESTA BASADA EN LOS DATOS DE {ubicacion_real.upper()}:
    """
        else:
            print("💬 Modo Normal - Sin exploración de archivos")
            contexto_herramienta = ""

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
                    if usar_herramienta:
                        modo = "MANUAL" if self.contexto_conversacion.get('ubicacion_manual') else "AUTOMÁTICO"
                        if termino_busqueda:
                            respuesta = f"🔍 (Búsqueda en {ubicacion_real}: '{termino_busqueda}', Profundidad: {profundidad}, Modo: {modo})\n{respuesta}"
                        else:
                            respuesta = f"🔍 (Explorando {ubicacion_real}, Profundidad: {profundidad}, Modo: {modo})\n{respuesta}"
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

    def activar_explorador_archivos(self, mensaje_usuario, profundidad=2, ubicacion_manual=None):
        """Activa manualmente el explorador de archivos"""
        print(f"🔧 Activación manual del explorador - Profundidad: {profundidad}")
        self.profundidad_actual = profundidad
        return self.generar_respuesta_ollama(mensaje_usuario, forzar_explorador=True, profundidad=profundidad,
                                             ubicacion_manual=ubicacion_manual)

    # ==================== MÉTODOS EXISTENTES (MANTENIDOS) ====================

    def cambiar_modelo(self, nuevo_modelo, callback_progreso=None):
        """Cambia el modelo actual"""
        if self.app_cerrando:
            return "❌ Aplicación cerrándose...", "error"

        modelos_compatibles = self.config_manager.obtener_modelos_compatibles()
        if nuevo_modelo not in modelos_compatibles:
            return f"❌ Modelo no compatible", "error"

        if self.gestor_modelos.verificar_modelo_instalado(nuevo_modelo):
            self.config["ollama_model"] = nuevo_modelo
            self.config_manager.guardar_configuracion()
            velocidad = modelos_compatibles[nuevo_modelo]["timeout"]
            return f"✅ Cambiado a {nuevo_modelo} (⏱️ {velocidad}s)", "success"

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