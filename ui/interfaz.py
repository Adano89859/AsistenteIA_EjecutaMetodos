import gradio as gr
import speech_recognition as sr
import time
import threading


def construir_interfaz(asistente):
    """Construye la nueva interfaz con 3 columnas"""

    with gr.Blocks(theme=gr.themes.Soft(), title="🧠 Asistente IA") as demo:
        # TÍTULO PRINCIPAL
        gr.Markdown("# 🧠 Asistente IA")

        with gr.Row():
            # ============================================================
            # COLUMNA IZQUIERDA - AYUDA AL USUARIO
            # ============================================================
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("### 💡 Ayuda para el usuario")

                with gr.Accordion("📋 Cómo usar la interfaz", open=True):
                    gr.Markdown("""
                    **Modos de operación:**
                    - **Normal**: Respuestas estándar de IA
                    - **Archivos**: Analiza tu sistema de archivos  
                    - **Rendimiento**: Métricas del sistema en tiempo real

                    **Controles de voz:**
                    - 🎤 Usar micrófono para dictar mensajes
                    - 🔊 Activar/desactivar voz de la IA

                    **Búsqueda avanzada:**
                    - Selecciona ubicación específica para búsquedas
                    - Controla la profundidad de exploración
                    """)

                # Terminal/output del sistema
                with gr.Accordion("📟 Terminal del sistema", open=False):
                    terminal_output = gr.Textbox(
                        label="Logs del sistema",
                        lines=8,
                        max_lines=12,
                        interactive=False,
                        value="✅ Sistema iniciado correctamente\n💬 Esperando tu mensaje..."
                    )

            # ============================================================
            # COLUMNA CENTRAL - CHAT PRINCIPAL (PROTAGONISTA)
            # ============================================================
            with gr.Column(scale=2, min_width=500):
                # CHATBOT - ÁREA PRINCIPAL
                chatbot = gr.Chatbot(
                    label="💬 Conversación",
                    height=450,
                    show_copy_button=True,
                    show_share_button=True,
                    avatar_images=(
                        "https://em-content.zobj.net/source/microsoft/319/robot_1f916.png",
                        "https://em-content.zobj.net/source/microsoft/319/brain_1f9e0.png"
                    )
                )

                # SECCIÓN INFERIOR - CONTROLES DE CHAT
                with gr.Row():
                    with gr.Column(scale=4):
                        txt_mensaje = gr.Textbox(
                            placeholder="Escribe tu mensaje aquí...",
                            label="",
                            show_label=False,
                            container=False
                        )

                    with gr.Column(scale=1):
                        btn_enviar = gr.Button("🚀 Enviar", variant="primary", size="lg")

                # BOTONES INFERIORES
                with gr.Row():
                    btn_limpiar_chat = gr.Button("🧹 Limpiar chat", size="sm")
                    btn_usar_microfono = gr.Button("🎤 Usar micrófono", size="sm")
                    gr.HTML("<div style='flex-grow: 1'></div>")  # Espacio flexible
                    estado_progreso = gr.Textbox(
                        label="",
                        value="✅ Listo",
                        interactive=False,
                        show_label=False,
                        scale=2
                    )

            # ============================================================
            # COLUMNA DERECHA - CONFIGURACIÓN AVANZADA
            # ============================================================
            with gr.Column(scale=1, min_width=300):
                gr.Markdown("### ⚙️ Configuración")

                # SECCIÓN SUPERIOR - CONTROLES BÁSICOS
                with gr.Row():
                    tipo_ayuda_dropdown = gr.Dropdown(
                        choices=["Normal", "Archivos del sistema", "Rendimiento del sistema"],
                        value="Normal",
                        label="Tipo de ayuda",
                        scale=2
                    )

                    personalidad_dropdown = gr.Dropdown(
                        choices=list(asistente.obtener_personalidades().keys()),
                        value=asistente.personalidad_actual,
                        label="Personalidad",
                        scale=2
                    )

                # CONTROLES DE AUDIO EN LÍNEA
                with gr.Row():
                    btn_toggle_voz = gr.Button("🔊 Voz", size="sm")
                    btn_toggle_mic = gr.Button("🎤 Mic", size="sm")
                    estado_audio = gr.Textbox(
                        value=f"{'🔊' if asistente.voz_activada else '🔇'} {'🎤' if asistente.microfono_activado else '🚫'}",
                        label="",
                        interactive=False,
                        show_label=False,
                        max_lines=1,
                        scale=1
                    )

                # AJUSTES AVANZADOS (Acordeón)
                with gr.Accordion("🔧 Ajustes avanzados", open=True):
                    # Selector de modelo
                    selector_modelos = gr.Dropdown(
                        choices=list(asistente.obtener_modelos_compatibles().keys()),
                        value=asistente.config["ollama_model"],
                        label="Modelo de IA",
                        info="Selecciona el modelo a utilizar"
                    )

                    btn_aplicar_modelo = gr.Button("🔄 Aplicar modelo", variant="secondary")

                    estado_modelo = gr.Textbox(
                        value="✅ LISTO" if asistente.verificar_modelo_instalado(
                            asistente.config["ollama_model"]) else "❌ NO INSTALADO",
                        label="Estado del modelo",
                        interactive=False
                    )

                    # Configuración de búsqueda
                    ubicacion_manual = gr.Dropdown(
                        choices=["automático", "usuario", "escritorio", "documentos",
                                 "descargas", "imágenes", "música", "vídeos"],
                        value="automático",
                        label="📍 Ubicación de búsqueda",
                        info="Dónde buscará la IA"
                    )

                    profundidad_busqueda = gr.Slider(
                        minimum=0,
                        maximum=5,
                        value=2,
                        step=1,
                        label="🔍 Profundidad de búsqueda",
                        info="Niveles de subcarpetas a explorar (0-5)"
                    )

                # BOTÓN DE CERRADO
                btn_cerrar = gr.Button("🛑 Cerrar aplicación", variant="stop")

        # ==================== EVENT HANDLERS ====================

        def enviar_mensaje(mensaje, historial, tipo_ayuda, profundidad, ubicacion):
            """Maneja el envío de mensajes"""
            if not mensaje.strip():
                return "", historial, "✏️ Escribe un mensaje..."

            historial.append([mensaje, "⏳ Procesando..."])

            # Actualizar estado
            estado = "🔄 Procesando tu mensaje..."

            # Lógica de modos
            if tipo_ayuda == "Archivos del sistema":
                print("🔧 Modo: Archivos del sistema - Activando explorador...")
                respuesta = asistente.activar_explorador_archivos(mensaje, profundidad, ubicacion)
            elif tipo_ayuda == "Rendimiento del sistema":
                print("📊 Modo: Rendimiento - Obteniendo métricas del sistema...")
                respuesta = asistente.obtener_rendimiento_sistema(mensaje)
            else:
                print("💬 Modo: Normal - Respuesta estándar")
                respuesta = asistente.generar_respuesta_ollama(mensaje, forzar_explorador=False)

            historial[-1] = [mensaje, respuesta]
            return "", historial, "✅ Listo"

        # Handler para enviar mensaje
        btn_enviar.click(
            enviar_mensaje,
            [txt_mensaje, chatbot, tipo_ayuda_dropdown, profundidad_busqueda, ubicacion_manual],
            [txt_mensaje, chatbot, estado_progreso]
        )

        txt_mensaje.submit(
            enviar_mensaje,
            [txt_mensaje, chatbot, tipo_ayuda_dropdown, profundidad_busqueda, ubicacion_manual],
            [txt_mensaje, chatbot, estado_progreso]
        )

        # Limpiar chat
        def limpiar_chat():
            return [], "💬 Chat limpiado"

        btn_limpiar_chat.click(
            limpiar_chat,
            outputs=[chatbot, estado_progreso]
        )

        # Microfono
        def escuchar_voz():
            if not asistente.microfono_activado:
                return "🚫 Mic desactivado", "🔇 Micrófono desactivado"
            try:
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    audio = r.listen(source, timeout=5)
                texto = r.recognize_google(audio, language="es-ES")
                return texto, "🎤 Voz detectada"
            except sr.WaitTimeoutError:
                return "❌ No se detectó voz", "⏰ Tiempo agotado"
            except:
                return "❌ Error de reconocimiento", "❌ Error de audio"

        btn_usar_microfono.click(
            escuchar_voz,
            outputs=[txt_mensaje, estado_progreso]
        )

        # Controles de audio
        def toggle_voz_handler():
            estado, mensaje = asistente.toggle_voz()
            icono = "🔊" if asistente.voz_activada else "🔇"
            estado_actual = f"{icono} {'🎤' if asistente.microfono_activado else '🚫'}"
            return estado_actual, mensaje

        btn_toggle_voz.click(
            toggle_voz_handler,
            outputs=[estado_audio, estado_progreso]
        )

        def toggle_mic_handler():
            estado, mensaje = asistente.toggle_microfono()
            icono = "🎤" if asistente.microfono_activado else "🚫"
            estado_actual = f"{'🔊' if asistente.voz_activada else '🔇'} {icono}"
            return estado_actual, mensaje

        btn_toggle_mic.click(
            toggle_mic_handler,
            outputs=[estado_audio, estado_progreso]
        )

        # Cambiar tipo de ayuda
        def cambiar_tipo_ayuda(tipo_seleccionado):
            if tipo_seleccionado == "Archivos del sistema":
                return "🔧 Modo: Archivos del sistema activado"
            elif tipo_seleccionado == "Rendimiento del sistema":
                return "📊 Modo: Rendimiento activado"
            else:
                return "💬 Modo: Normal activado"

        tipo_ayuda_dropdown.change(
            cambiar_tipo_ayuda,
            [tipo_ayuda_dropdown],
            [estado_progreso]
        )

        # Cambiar personalidad
        def cambiar_personalidad(nueva):
            asistente.personalidad_actual = nueva
            asistente.config["personalidad_actual"] = nueva
            asistente.config_manager.guardar_configuracion()
            return f"✅ Personalidad: {nueva}"

        personalidad_dropdown.change(
            cambiar_personalidad,
            [personalidad_dropdown],
            [estado_progreso]
        )

        # Cambiar ubicación
        def cambiar_ubicacion_manual(ubicacion):
            if ubicacion == "automático":
                return "📍 Ubicación: Automático"
            else:
                return f"📍 Ubicación: {ubicacion.title()}"

        ubicacion_manual.change(
            cambiar_ubicacion_manual,
            [ubicacion_manual],
            [estado_progreso]
        )

        # Cambiar modelo
        def cambiar_modelo_handler(modelo_seleccionado):
            if not modelo_seleccionado:
                return "❌ Selecciona un modelo", asistente.config["ollama_model"], "❌ Error"

            resultado, tipo = asistente.cambiar_modelo(modelo_seleccionado)

            time.sleep(1)
            if tipo == "success":
                nuevo_estado = "✅ LISTO"
                mensaje_estado = f"✅ Modelo cambiado a {modelo_seleccionado}"
            else:
                nuevo_estado = "📥 DESCARGANDO..." if tipo == "download" else "❌ ERROR"
                mensaje_estado = resultado

            return resultado, modelo_seleccionado, nuevo_estado, mensaje_estado

        btn_aplicar_modelo.click(
            cambiar_modelo_handler,
            [selector_modelos],
            [estado_modelo, selector_modelos, estado_modelo, estado_progreso]
        )

        # Cerrar aplicación
        def cerrar_app():
            print("🛑 Cerrando aplicación...")
            asistente.app_cerrando = True
            asistente.silenciar_voz_actual()
            asistente.config_manager.guardar_configuracion()

            def cerrar_forzado():
                time.sleep(1)
                import os
                os._exit(0)

            threading.Thread(target=cerrar_forzado, daemon=True).start()
            return "🛑 Cerrando..."

        btn_cerrar.click(cerrar_app, outputs=[estado_progreso])

    return demo