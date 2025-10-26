#!/usr/bin/env python3
"""
Verificador de configuración del Asistente IA
"""

import json
import os
import sys


def verificar_configuracion():
    """Verifica que la configuración sea correcta"""

    config_file = os.path.join("config", "config.json")

    print("🔍 VERIFICANDO CONFIGURACIÓN...")
    print(f"📁 Archivo: {config_file}")

    if not os.path.exists(config_file):
        print("❌ No existe archivo de configuración")
        return False

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        modelo = config.get('ollama_model', 'NO CONFIGURADO')
        print(f"🤖 Modelo configurado: {modelo}")

        # Verificar que Ollama tiene el modelo
        import requests
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                modelos = response.json().get('models', [])
                modelos_nombres = [m.get('name', '') for m in modelos]

                if any(modelo in nombre for nombre in modelos_nombres):
                    print("✅ Modelo detectado en Ollama")
                    return True
                else:
                    print(f"⚠️ Modelo {modelo} no encontrado en Ollama")
                    print(f"📋 Modelos disponibles: {[m.get('name') for m in modelos]}")
                    return False
            else:
                print("❌ Ollama no responde")
                return False

        except Exception as e:
            print(f"❌ Error conectando con Ollama: {e}")
            return False

    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        return False


if __name__ == "__main__":
    verificar_configuracion()