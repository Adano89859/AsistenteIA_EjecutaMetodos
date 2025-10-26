import os
import fnmatch


class ExploradorArchivos:
    """Sistema OPTIMIZADO para explorar archivos usando PYTHON PURO"""

    @staticmethod
    def obtener_estructura_carpetas(ruta_inicio=None, buscar_nombre=None, profundidad_maxima=3):
        """Obtiene estructura con control de profundidad"""
        try:
            # 1. OBTENER RUTA REAL DEL USUARIO
            usuario_real = os.getlogin()
            carpeta_usuario_real = os.path.expanduser("~")

            print(f"👤 Usuario detectado: {usuario_real}")
            print(f"📁 Carpeta usuario: {carpeta_usuario_real}")

            # 2. RUTAS CON NOMBRES REALES
            rutas_permitidas = {
                # Español
                "usuario": carpeta_usuario_real,
                "escritorio": os.path.join(carpeta_usuario_real, "Desktop"),
                "documentos": os.path.join(carpeta_usuario_real, "Documents"),
                "descargas": os.path.join(carpeta_usuario_real, "Downloads"),
                "imágenes": os.path.join(carpeta_usuario_real, "Pictures"),
                "música": os.path.join(carpeta_usuario_real, "Music"),
                "vídeos": os.path.join(carpeta_usuario_real, "Videos"),

                # Inglés
                "user": carpeta_usuario_real,
                "desktop": os.path.join(carpeta_usuario_real, "Desktop"),
                "documents": os.path.join(carpeta_usuario_real, "Documents"),
                "downloads": os.path.join(carpeta_usuario_real, "Downloads"),
                "pictures": os.path.join(carpeta_usuario_real, "Pictures"),
                "music": os.path.join(carpeta_usuario_real, "Music"),
                "videos": os.path.join(carpeta_usuario_real, "Videos"),

                # Otros
                "actual": os.getcwd(),
                "current": os.getcwd(),
                "ordenador": "C:\\",
                "computer": "C:\\",
                "proyecto": os.path.dirname(os.path.abspath(__file__)),
                "project": os.path.dirname(os.path.abspath(__file__))
            }

            # 3. RUTA POR DEFECTO
            if not ruta_inicio:
                ruta_inicio = "usuario"

            ruta_real = rutas_permitidas.get(ruta_inicio.lower(), ruta_inicio)

            # Validar que la ruta existe
            if not os.path.exists(ruta_real):
                return f"❌ La ruta no existe: {ruta_real}"

            print(f"🔍 Explorando con PYTHON: {ruta_real} - Profundidad: {profundidad_maxima}")

            # 4. EXPLORACIÓN CON PROFUNDIDAD CONTROLADA
            return ExploradorArchivos._explorar_con_python(ruta_real, buscar_nombre, profundidad_maxima)

        except Exception as e:
            return f"❌ Error: {str(e)}"

    @staticmethod
    def _explorar_con_python(ruta_absoluta, buscar_nombre, profundidad_maxima):
        """Exploración que RESPETA la profundidad máxima"""
        estadisticas = {
            'total_archivos': 0,
            'total_carpetas': 0,
            'archivos_por_tipo': {},
            'estructura': {
                'raiz': {
                    'carpetas': [],
                    'archivos': []
                },
                'subdirectorios': {}
            },
            'coincidencias': [],
            'carpeta_raiz': os.path.basename(ruta_absoluta),
            'profundidad_maxima': profundidad_maxima
        }

        try:
            for raiz, directorios, archivos in os.walk(ruta_absoluta):
                nivel = raiz.replace(ruta_absoluta, '').count(os.sep)
                ruta_relativa = os.path.relpath(raiz, ruta_absoluta)

                # ✅ FILTRAR POR PROFUNDIDAD MÁXIMA
                if nivel > profundidad_maxima:
                    continue  # Saltar niveles más profundos

                # ✅ LIMITAR SUBDIRECTORIOS SI ESTAMOS EN EL LÍMITE
                if nivel == profundidad_maxima:
                    directorios.clear()  # No explorar más allá de este nivel

                estadisticas['total_carpetas'] += 1
                estadisticas['total_archivos'] += len(archivos)

                # ✅ DIFERENCIAR POR NIVEL
                if nivel == 0:  # DIRECTORIO RAÍZ
                    # Carpeta raíz
                    estadisticas['estructura']['raiz']['carpetas'] = directorios
                    estadisticas['estructura']['raiz']['archivos'] = archivos

                else:  # SUBDIRECTORIOS
                    # Guardar información del subdirectorio actual
                    if ruta_relativa not in estadisticas['estructura']['subdirectorios']:
                        estadisticas['estructura']['subdirectorios'][ruta_relativa] = {
                            'nivel': nivel,
                            'carpetas': directorios,
                            'archivos': archivos
                        }

                # Procesar archivos manteniendo información del nivel
                for archivo in archivos:
                    extension = os.path.splitext(archivo)[1].lower()
                    conteo_actual = estadisticas['archivos_por_tipo'].get(extension, 0)
                    estadisticas['archivos_por_tipo'][extension] = conteo_actual + 1

                    # Búsqueda con información de RUTA COMPLETA (en lugar de nivel)
                    if buscar_nombre and buscar_nombre.lower() in archivo.lower():
                        ruta_completa = os.path.join(raiz, archivo)
                        # CAMBIO AQUÍ: Usar ruta_relativa en lugar de nivel numérico
                        tipo = "archivo_raiz" if nivel == 0 else "archivo_subdirectorio"
                        estadisticas['coincidencias'].append({
                            'tipo': tipo,
                            'nombre': archivo,
                            'ruta': ruta_relativa,  # Esta ya contiene la ruta completa relativa
                            'nivel': nivel,
                            'ruta_completa': ruta_completa
                        })

                # Procesar carpetas con información de RUTA COMPLETA
                for carpeta in directorios:
                    if buscar_nombre and buscar_nombre.lower() in carpeta.lower():
                        # CAMBIO AQUÍ: Usar ruta_relativa en lugar de nivel numérico
                        tipo = "carpeta_raiz" if nivel == 0 else "carpeta_subdirectorio"
                        estadisticas['coincidencias'].append({
                            'tipo': tipo,
                            'nombre': carpeta,
                            'ruta': ruta_relativa,  # Esta ya contiene la ruta completa relativa
                            'nivel': nivel
                        })

            # Esta parte es para yo ver la información por terminal
            print(ExploradorArchivos._generar_reporte_inteligente(ruta_absoluta, estadisticas, buscar_nombre))
            return ExploradorArchivos._generar_reporte_inteligente(ruta_absoluta, estadisticas, buscar_nombre)

        except Exception as e:
            return f"❌ Error en exploración: {str(e)}"

    @staticmethod
    def _generar_reporte_inteligente(ruta, estadisticas, buscar_nombre):
        """Genera reporte que incluye información de profundidad"""
        # ✅ CORREGIDO: Indentación correcta
        reporte = f"""
📊 **ANÁLISIS JERÁRQUICO DEL SISTEMA DE ARCHIVOS**
📍 **Ubicación:** {ruta}
👤 **Usuario:** {os.getlogin()}
🔍 **Profundidad de análisis:** {estadisticas.get('profundidad_maxima', 'Completa')} niveles

📁 **ESTADÍSTICAS GENERALES:**
• Carpetas analizadas: {estadisticas['total_carpetas']:,}
• Archivos encontrados: {estadisticas['total_archivos']:,}
"""

        # ... (el resto del método permanece igual) ...
        # ✅ MOSTRAR CONTENIDO DEL DIRECTORIO RAÍZ
        if 'estructura' in estadisticas and estadisticas['estructura']['raiz']:
            raiz = estadisticas['estructura']['raiz']
            reporte += f"\n📂 **CONTENIDO DEL DIRECTORIO RAÍZ:**"

            # Mostrar carpetas del directorio raíz
            for carpeta in raiz['carpetas']:
                reporte += f"\n• 📁 {carpeta}/"

            # Mostrar archivos del directorio raíz
            for archivo in raiz['archivos']:
                extension = os.path.splitext(archivo)[1].lower()
                icono = ExploradorArchivos._obtener_icono_archivo(extension)
                reporte += f"\n• {icono} {archivo}"

            if len(raiz['carpetas']) > 10 or len(raiz['archivos']) > 10:
                reporte += f"\n• ... y otros {max(0, len(raiz['carpetas']) - 10) + max(0, len(raiz['archivos']) - 10)} elementos más"

        # ✅ INFORMACIÓN DE SUBDIRECTORIOS (RECURSIVO)
        if 'estructura' in estadisticas and estadisticas['estructura']['subdirectorios']:
            reporte += f"\n\n📂 **INFORMACIÓN DE SUBDIRECTORIOS:**"

            # Ordenar subdirectorios por nivel para mejor organización
            subdirs_ordenados = sorted(estadisticas['estructura']['subdirectorios'].items(),
                                       key=lambda x: x[1]['nivel'])

            for subdir, info in subdirs_ordenados:
                # Mostrar el subdirectorio actual
                reporte += f"\n\n• 📁 {subdir}/"
                reporte += f"\n  └── Nivel: {info['nivel']}"

                # Mostrar subcarpetas dentro de este subdirectorio
                if info['carpetas']:
                    reporte += f"\n  └── 📂 Subcarpetas:"
                    for carpeta in info['carpetas']:
                        ruta_completa_carpeta = os.path.join(subdir, carpeta)
                        reporte += f"\n      • 📁 {ruta_completa_carpeta}/"

                # Mostrar archivos dentro de este subdirectorio
                if info['archivos']:
                    reporte += f"\n  └── 📄 Archivos:"
                    for archivo in info['archivos']:
                        nombre_archivo = os.path.join(archivo)
                        reporte += f"\n      • {nombre_archivo}"

        # ... (resto del método igual) ...

        return reporte

    @staticmethod
    def _obtener_icono_archivo(extension):
        """Devuelve un icono apropiado para el tipo de archivo"""
        iconos = {
            '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨',
            '.json': '📋', '.txt': '📄', '.md': '📝',
            '.jpg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.svg': '🖼️',
            '.mp4': '🎥', '.avi': '🎥', '.mkv': '🎥',
            '.mp3': '🎵', '.wav': '🎵', '.flac': '🎵',
            '.pdf': '📕', '.doc': '📘', '.docx': '📘',
            '.xls': '📗', '.xlsx': '📗', '.ppt': '📙', '.pptx': '📙',
            '.zip': '📦', '.rar': '📦', '.tar': '📦', '.gz': '📦',
            '.exe': '⚙️', '.dll': '🔧', '.ini': '⚙️', '.config': '⚙️',
            "carpeta":'📁'
        }
        return iconos.get(extension, '📄')