#!/usr/bin/env python3
"""
Asistente IA - VERSIÓN ULTRA RÁPIDA Y MODULAR
"""

import os
import sys
import warnings

# Configuración inicial
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

warnings.filterwarnings("ignore")
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

# Añadir rutas para imports
sys.path.insert(0, os.path.join(BASE_DIR, 'config'))
sys.path.insert(0, os.path.join(BASE_DIR, 'core'))
sys.path.insert(0, os.path.join(BASE_DIR, 'ui'))
sys.path.insert(0, os.path.join(BASE_DIR, 'utils'))
sys.path.insert(0, os.path.join(BASE_DIR, 'herramientas'))


def main():
    print("================================================")
    print("🧠 ASISTENTE IA - VERSIÓN MODULAR ULTRA RÁPIDA")
    print("================================================")

    try:
        from core.asistente import AsistenteIA
        from ui.interfaz import construir_interfaz

        asistente = AsistenteIA()
        demo = construir_interfaz(asistente)

        demo.launch(
            server_name="127.0.0.1",
            server_port=7860,
            show_error=True,
            share=False,
            inbrowser=True,
            show_api=False
        )

    except Exception as e:
        print(f"❌ Error iniciando aplicación: {e}")
        if getattr(sys, 'frozen', False):
            input("Presiona Enter para salir...")


if __name__ == "__main__":
    import multiprocessing

    multiprocessing.set_start_method("spawn", force=True)
    main()