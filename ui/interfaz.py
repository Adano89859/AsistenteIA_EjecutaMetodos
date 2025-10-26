import gradio as gr
import speech_recognition as sr
import time
import threading


def construir_interfaz(asistente):
    """Construye la interfaz con control de profundidad"""

    with gr.Blocks(theme=gr.themes.Soft(), title="🧠 Asistente IA ULTRA RÁPIDO") as demo:
        gr.Markdown("# 🧠 Asistente IA - 💭 VERSIÓN COMPLETA")
        gr.Markdown("**Sin límites - Respuestas completas y detalladas**")

        with gr.Row():
            # COLUMNA IZQUIERDA - CONFIGURACIÓN
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ CONFIGURACIÓN RÁPIDA")

                # Modelo actual
                modelo_actual = gr.Textbox(
                    value=f"{asistente.config['ollama_model']} - 💭 COMPLETO",
                    label="Modelo actual",
                    interactive=False
                )

                # Selector simple de modelos
                selector_modelos = gr.Dropdown(
                    choices=list(asistente.obtener_modelos_compatibles().keys()),
                    value=asistente.config["ollama_model"],
                    label="Cambiar modelo",
                    info="Todos los modelos = Respuestas completas"
                )

                btn_aplicar_modelo = gr.Button("⚡ APLICAR MODELO", variant="primary")

                estado_modelo = gr.Textbox(
                    value="✅ LISTO" if asistente.verificar_modelo_instalado(
                        asistente.config["ollama_model"]) else "❌ NO INSTALADO",
                    label="Estado",
                    interactive=False
                )

                progreso_descarga = gr.Textbox(
                    label="Progreso",
                    interactive=False,
                    value="⚡ Listo para chat rápido"
                )

                # Personalidad rápida
                personalidad_dropdown = gr.Dropdown(
                    choices=list(asistente.obtener_personalidades().keys()),
                    value=asistente.personalidad_actual,
                    label="Modo de respuesta",
                    info="Ambos modos = Respuestas sin límites"
                )

                # ✅ NUEVO: CONTROL DE PROFUNDIDAD DE BÚSQUEDA
                profundidad_busqueda = gr.Slider(
                    minimum=0,
                    maximum=5,
                    value=2,  # Valor por defecto
                    step=1,
                    label="🔍 Profundidad de búsqueda",
                    info="Niveles de subcarpetas a explorar"
                )

                # Selector de Tipo de Ayuda (MODIFICADO)
                tipo_ayuda_dropdown = gr.Dropdown(
                    choices=["Normal", "Archivos del sistema"],
                    value="Normal",
                    label="🔧 Tipo de Ayuda",
                    info="Selecciona el modo de respuesta"
                )

                # Controles simples
                with gr.Row():
                    btn_toggle_voz = gr.Button("🔊 Voz", size="sm")
                    btn_toggle_mic = gr.Button("🎤 Mic", size="sm")

                estado_controles = gr.Textbox(
                    value=f"Voz: {'🔊' if asistente.voz_activada else '🔇'} | Mic: {'🎤' if asistente.microfono_activado else '🚫'}",
                    label="Controles",
                    interactive=False
                )

                btn_cerrar = gr.Button("🛑 Cerrar", variant="stop")

            # COLUMNA DERECHA - CHAT
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="💬 CHAT RÁPIDO",
                    height=400,
                    show_copy_button=True
                )

                with gr.Row():
                    txt_mensaje = gr.Textbox(
                        placeholder="Escribe tu mensaje... (respuesta completa sin límites)",
                        label="Mensaje completo",
                        scale=4
                    )
                    btn_enviar = gr.Button("⚡ Enviar", variant="primary", scale=1)

                with gr.Row():
                    btn_limpiar = gr.Button("🗑️ Limpiar")
                    btn_microfono = gr.Button("🎤 Voz")

        # ==================== EVENT HANDLERS RÁPIDOS ====================

        def enviar_mensaje(mensaje, historial, tipo_ayuda, profundidad):
            if not mensaje.strip():
                return "", historial

            historial.append([mensaje, "⏳ Procesando..."])

            # ✅ PASAR LA PROFUNDIDAD AL ASISTENTE
            if tipo_ayuda == "Archivos del sistema":
                respuesta = asistente.activar_explorador_archivos(mensaje, profundidad)
            else:  # Modo Normal
                respuesta = asistente.generar_respuesta_ollama(mensaje)

            historial[-1] = [mensaje, respuesta]
            return "", historial

        # Actualizar los handlers para incluir profundidad
        btn_enviar.click(
            enviar_mensaje,
            [txt_mensaje, chatbot, tipo_ayuda_dropdown, profundidad_busqueda],
            [txt_mensaje, chatbot]
        )

        txt_mensaje.submit(
            enviar_mensaje,
            [txt_mensaje, chatbot, tipo_ayuda_dropdown, profundidad_busqueda],
            [txt_mensaje, chatbot]
        )

        # Limpiar chat
        btn_limpiar.click(lambda: [], outputs=[chatbot])

        # Microfono
        def escuchar_voz():
            if not asistente.microfono_activado:
                return "🚫 Mic desactivado"
            try:
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    audio = r.listen(source, timeout=5)
                return r.recognize_google(audio, language="es-ES")
            except:
                return "❌ No se detectó voz"

        btn_microfono.click(escuchar_voz, outputs=[txt_mensaje])

        # Controles
        def toggle_voz_handler():
            estado, mensaje = asistente.toggle_voz()
            return mensaje

        btn_toggle_voz.click(toggle_voz_handler, outputs=[estado_controles])

        def toggle_mic_handler():
            estado, mensaje = asistente.toggle_microfono()
            return mensaje

        btn_toggle_mic.click(toggle_mic_handler, outputs=[estado_controles])

        # Cambiar tipo de ayuda - Handler
        def cambiar_tipo_ayuda(tipo_seleccionado):
            """Actualiza el estado según el tipo de ayuda seleccionado"""
            if tipo_seleccionado == "Archivos del sistema":
                return "🔧 Modo: Archivos del sistema - La IA analizará tu sistema de archivos"
            else:
                return "🔧 Modo: Normal - Respuesta estándar"

        tipo_ayuda_dropdown.change(
            cambiar_tipo_ayuda,
            [tipo_ayuda_dropdown],
            [progreso_descarga]
        )

        # Cambiar personalidad
        def cambiar_personalidad(nueva):
            asistente.personalidad_actual = nueva
            asistente.config["personalidad_actual"] = nueva
            asistente.config_manager.guardar_configuracion()
            return f"✅ Modo: {nueva}"

        personalidad_dropdown.change(
            cambiar_personalidad,
            [personalidad_dropdown],
            [estado_controles]
        )

        # Cambiar modelo
        def cambiar_modelo_handler(modelo_seleccionado):
            if not modelo_seleccionado:
                return "❌ Selecciona modelo", asistente.config["ollama_model"], "Listo"

            resultado, tipo = asistente.cambiar_modelo(modelo_seleccionado)

            # Actualizar UI
            time.sleep(1)
            if tipo == "success":
                nuevo_estado = "✅ LISTO"
                modelo_display = f"{modelo_seleccionado} - ⚡ RÁPIDO"
            else:
                nuevo_estado = "📥 DESCARGANDO..." if tipo == "download" else "❌ ERROR"
                modelo_display = asistente.config["ollama_model"]

            return resultado, modelo_display, nuevo_estado

        btn_aplicar_modelo.click(
            cambiar_modelo_handler,
            [selector_modelos],
            [progreso_descarga, modelo_actual, estado_modelo]
        )

        # Cerrar aplicación
        def cerrar_app():
            print("🛑 Cerrando aplicación rápida...")
            asistente.app_cerrando = True
            asistente.silenciar_voz_actual()
            asistente.config_manager.guardar_configuracion()

            def cerrar_forzado():
                time.sleep(1)
                import os
                os._exit(0)

            threading.Thread(target=cerrar_forzado, daemon=True).start()
            return "🛑 Cerrando..."

        btn_cerrar.click(cerrar_app, outputs=[progreso_descarga])

    return demo