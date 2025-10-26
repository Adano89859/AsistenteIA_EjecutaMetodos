# 🧠 Asistente IA con Control de Voz

Una aplicación de chat inteligente con **voz bidireccional**, **personalidades múltiples** y **modo exportable**, creada con Gradio y Python.

---

## ✨ Características Principales

- 🤖 **Múltiples personalidades de IA** (Neutral, Alegre, Formal, Creativo, Técnico, Minimalista)
- 🔊 **Voz natural con interrupciones en tiempo real**
- 🎤 **Reconocimiento automático de voz**
- 💬 **Chat interactivo local o en red**
- 🎨 **Interfaz moderna y adaptable**
- ⚙️ **Configuración persistente entre sesiones**
- 🧩 **Instalador y lanzador automático (.bat)**
- 💻 **Modo ejecutable o desarrollo (según entorno)**

---

## 🔧 Requisitos del Sistema

| Requisito | Detalle |
|------------|----------|
| 🪟 Sistema | Windows 10 o 11 |
| 🐍 Python  | 3.8 o superior |
| 💾 RAM     | 4 GB mínimo (8 GB recomendado) |
| 🌐 Internet | Solo necesario para reconocimiento de voz |
| 🎙️ Micrófono | Requerido para control por voz |

---

## 🚀 Instalación y Uso

### 🧩 Opción 1 — Método automático (recomendado)

1. Ejecuta `install.bat`
2. Espera a que se compile y configure la aplicación.
3. Se creará una carpeta `dist/` con los archivos listos.
4. Un acceso directo **“Asistente IA”** aparecerá en tu Escritorio.
5. Haz doble clic en él para iniciar la app.

💡 Si el ejecutable (`.exe`) falla, el acceso directo usa el **modo seguro** con `ejecutar_app.bat`, que ejecuta el código fuente directamente con Python.

---

### 🧠 Opción 2 — Desde código fuente

```bash
# 1. Instala dependencias
pip install -r requirements.txt

# 2. Ejecuta la aplicación
python main.py
🔹 Para acceso en red local:

bash
Copiar código
python main.py --network
Luego abre en el navegador:

http://[IP-DEL-ORDENADOR]:7860



🧰 Archivos Principales del Proyecto
bash
Copiar código
AsistenteIA/
├── main.py                 # Aplicación principal
├── ejecutar_app.bat        # Lanzador seguro (modo fallback)
├── install.bat             # Instalador con creador de acceso directo
├── requirements.txt        # Dependencias
├── assets/
│   └── icon.ico            # Icono de la aplicación
├── config/
│   └── config.json         # Configuración persistente
└── historial_chat.json     # Historial de conversaciones
🩺 Solución de Problemas
❌ Error: “safehttpx/version.txt not found”
Ocurre en el modo ejecutable.
✅ Solución: El lanzador ejecutar_app.bat detecta este error y ejecuta automáticamente el código fuente real.

❌ Error de voz
Asegúrate de tener voces instaladas en el sistema.

Revisa los controladores de audio.

❌ Error de micrófono
Verifica permisos de acceso al micrófono.

Comprueba que esté configurado como dispositivo predeterminado.

❌ Error de Ollama
Ejecuta: ollama serve

Verifica modelos disponibles: ollama list

Descarga uno: ollama pull gemma3:4b

🧩 Características Técnicas
Configuración persistente (voz, personalidad, ajustes)

Recuperación automática tras errores

Interfaz moderna con Gradio

Scripts .bat automáticos para instalación y ejecución

Exportable y sin dependencias externas una vez compilado

📞 Soporte
Si tienes problemas:

Revisa este README

Verifica dependencias y versiones

Asegúrate de usar Python 3.8 o superior

💬 Hecho con Python, Gradio y mucha paciencia.
🚀 Disfruta de tu Asistente IA conversacional con voz bidireccional.

yaml
Copiar código

---

¿Quieres que el acceso directo del instalador (el `.lnk`) tenga **nombre e icono personalizados** (por ejemplo “🧠 Asistente IA” con el icono `assets/icon.ico`)?  
Puedo añadir eso directamente en la línea del acceso directo para que aparezca con emoji y estilo moderno en el Escritorio.






