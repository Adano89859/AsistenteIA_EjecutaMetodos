import os
import fnmatch
import re


class ExploradorArchivos:
    """Sistema OPTIMIZADO para explorar archivos usando PYTHON PURO"""

    @staticmethod
    def obtener_estructura_carpetas(ruta_inicio=None, buscar_nombre=None, profundidad_maxima=3):
        """Obtiene estructura con control de profundidad Y búsqueda inteligente"""
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

            # ✅ NUEVO: Diferencia entre exploración completa y búsqueda específica
            if buscar_nombre:
                print(f"🎯 BÚSQUEDA ACTIVADA: '{buscar_nombre}'")
                return ExploradorArchivos._explorar_con_busqueda_especifica(ruta_real, buscar_nombre,
                                                                            profundidad_maxima)
            else:
                print("📊 EXPLORACIÓN COMPLETA (sin búsqueda específica)")
                return ExploradorArchivos._explorar_con_python(ruta_real, None, profundidad_maxima)

        except Exception as e:
            return f"❌ Error: {str(e)}"

    @staticmethod
    def _explorar_con_busqueda_especifica(ruta_absoluta, termino_busqueda, profundidad_maxima):
        """Exploración OPTIMIZADA que solo busca coincidencias específicas"""
        estadisticas = {
            'total_coincidencias': 0,
            'coincidencias_detalladas': [],
            'termino_busqueda': termino_busqueda,
            'profundidad_maxima': profundidad_maxima,
            'ubicacion': ruta_absoluta
        }

        try:
            for raiz, directorios, archivos in os.walk(ruta_absoluta):
                nivel = raiz.replace(ruta_absoluta, '').count(os.sep)
                ruta_relativa = os.path.relpath(raiz, ruta_absoluta)

                # ✅ FILTRAR POR PROFUNDIDAD MÁXIMA
                if nivel > profundidad_maxima:
                    continue

                # ✅ LIMITAR SUBDIRECTORIOS SI ESTAMOS EN EL LÍMITE
                if nivel == profundidad_maxima:
                    directorios.clear()

                # ✅ BUSCAR CARPETAS QUE COINCIDAN
                for carpeta in directorios:
                    if termino_busqueda.lower() in carpeta.lower():
                        estadisticas['total_coincidencias'] += 1
                        estadisticas['coincidencias_detalladas'].append({
                            'tipo': 'carpeta',
                            'nombre': carpeta,
                            'ruta': ruta_relativa,
                            'nivel': nivel,
                            'ruta_completa': os.path.join(raiz, carpeta)
                        })

                # ✅ BUSCAR ARCHIVOS QUE COINCIDAN
                for archivo in archivos:
                    if termino_busqueda.lower() in archivo.lower():
                        estadisticas['total_coincidencias'] += 1
                        extension = os.path.splitext(archivo)[1].lower()
                        estadisticas['coincidencias_detalladas'].append({
                            'tipo': 'archivo',
                            'nombre': archivo,
                            'extension': extension,
                            'ruta': ruta_relativa,
                            'nivel': nivel,
                            'ruta_completa': os.path.join(raiz, archivo)
                        })

            # ✅ GENERAR REPORTE ESPECÍFICO PARA BÚSQUEDA
            return ExploradorArchivos._generar_reporte_busqueda(estadisticas)

        except Exception as e:
            return f"❌ Error en búsqueda: {str(e)}"

    @staticmethod
    def _generar_reporte_busqueda(estadisticas):
        """Genera reporte ESPECÍFICO para resultados de búsqueda"""

        termino = estadisticas['termino_busqueda']
        total = estadisticas['total_coincidencias']
        ubicacion = estadisticas['ubicacion']
        profundidad = estadisticas['profundidad_maxima']

        reporte = f"""
🎯 **BÚSQUEDA ESPECÍFICA: '{termino.upper()}'**
📍 **Ubicación:** {ubicacion}
🔍 **Profundidad:** {profundidad} niveles
📊 **Total de coincidencias:** {total}

"""

        if total == 0:
            reporte += "❌ **No se encontraron coincidencias**"
            return reporte

        # ✅ ORGANIZAR RESULTADOS POR TIPO
        carpetas = [c for c in estadisticas['coincidencias_detalladas'] if c['tipo'] == 'carpeta']
        archivos = [c for c in estadisticas['coincidencias_detalladas'] if c['tipo'] == 'archivo']

        if carpetas:
            reporte += f"\n📂 **CARPETAS ENCONTRADAS ({len(carpetas)}):**\n"
            for carpeta in carpetas:
                ubicacion_desc = "📍 RAÍZ" if carpeta['nivel'] == 0 else f"📁 Subnivel {carpeta['nivel']}"
                if carpeta['ruta'] != '.':
                    reporte += f"• 📁 {carpeta['nombre']}\n  └── {ubicacion_desc} (Ruta: {carpeta['ruta']})\n"
                else:
                    reporte += f"• 📁 {carpeta['nombre']}\n  └── {ubicacion_desc}\n"

        if archivos:
            reporte += f"\n📄 **ARCHIVOS ENCONTRADOS ({len(archivos)}):**\n"
            for archivo in archivos:
                icono = ExploradorArchivos._obtener_icono_archivo(archivo['extension'])
                ubicacion_desc = "📍 RAÍZ" if archivo['nivel'] == 0 else f"📁 Subnivel {archivo['nivel']}"
                if archivo['ruta'] != '.':
                    reporte += f"• {icono} {archivo['nombre']}\n  └── {ubicacion_desc} (Ruta: {archivo['ruta']})\n"
                else:
                    reporte += f"• {icono} {archivo['nombre']}\n  └── {ubicacion_desc}\n"

        # ✅ RESUMEN EJECUTIVO
        reporte += f"\n💡 **RESUMEN EJECUTIVO:**"
        reporte += f"\n• Término buscado: '{termino}'"
        reporte += f"\n• Coincidencias totales: {total}"
        if carpetas:
            reporte += f"\n• Carpetas encontradas: {len(carpetas)}"
        if archivos:
            reporte += f"\n• Archivos encontrados: {len(archivos)}"
        reporte += f"\n• Búsqueda completada: ✅ ÉXITO"

        return reporte

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
        reporte = f"""
📊 **ANÁLISIS JERÁRQUICO DEL SISTEMA DE ARCHIVOS**
📍 **Ubicación:** {ruta}
👤 **Usuario:** {os.getlogin()}
🔍 **Profundidad de análisis:** {estadisticas.get('profundidad_maxima', 'Completa')} niveles

📁 **ESTADÍSTICAS GENERALES:**
• Carpetas analizadas: {estadisticas['total_carpetas']:,}
• Archivos encontrados: {estadisticas['total_archivos']:,}
"""

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

        # ✅ BÚSQUEDA CON INFORMACIÓN DE RUTA (EN LUGAR DE NIVEL NUMÉRICO)
        if buscar_nombre and estadisticas['coincidencias']:
            reporte += f"\n\n🎯 **BÚSQUEDA: '{buscar_nombre.upper()}' - RESULTADOS:**"

            # Separar por ubicación (raíz vs subdirectorios)
            coincidencias_raiz = [c for c in estadisticas['coincidencias'] if c['nivel'] == 0]
            coincidencias_subniveles = [c for c in estadisticas['coincidencias'] if c['nivel'] > 0]

            # Mostrar coincidencias en directorio raíz
            if coincidencias_raiz:
                reporte += f"\n\n📍 **EN DIRECTORIO RAÍZ:**"
                for coinci in coincidencias_raiz:
                    icono = "📁" if coinci['tipo'].startswith('carpeta') else ExploradorArchivos._obtener_icono_archivo(
                        os.path.splitext(coinci['nombre'])[1])
                    reporte += f"\n• {icono} {coinci['nombre']}"

            # Mostrar coincidencias en subdirectorios - AHORA CON RUTA COMPLETA
            if coincidencias_subniveles:
                reporte += f"\n\n📂 **EN SUBDIRECTORIOS:**"
                for coinci in coincidencias_subniveles:
                    icono = "📁" if coinci['tipo'].startswith(
                        'carpeta') else ExploradorArchivos._obtener_icono_archivo(
                        os.path.splitext(coinci['nombre'])[1])
                    # CAMBIO CLAVE AQUÍ: Mostrar la ruta completa en lugar del nivel numérico
                    if coinci['ruta'] != '.':  # Si no es el directorio raíz
                        reporte += f"\n• {icono} {coinci['ruta']}/{coinci['nombre']}"
                    else:
                        reporte += f"\n• {icono} {coinci['nombre']}"

            # Resumen de búsqueda
            total_coincidencias = len(coincidencias_raiz) + len(coincidencias_subniveles)
            if total_coincidencias > 15:  # Si hay muchas coincidencias
                reporte += f"\n• ... y {total_coincidencias - 15} resultados más"

        # ✅ MANTENER: TIPOS DE ARCHIVOS PRINCIPALES (esta parte sigue igual)
        if estadisticas['archivos_por_tipo']:
            reporte += f"\n\n📋 **TIPOS DE ARCHIVOS Y SUS CANTIDADES:**"
            tipos_comunes = sorted(
                estadisticas['archivos_por_tipo'].items(),
                key=lambda x: x[1],
                reverse=True
            )

            for extension, cantidad in tipos_comunes:
                if extension:  # Con extensión
                    icono = ExploradorArchivos._obtener_icono_archivo(extension)
                    reporte += f"\n• {icono} {extension}: {cantidad:,}"
                else:  # Sin extensión
                    icono = ExploradorArchivos._obtener_icono_archivo("carpeta")
                    reporte += f"\n• {icono} sin extensión: {cantidad:,}"

        # ✅ MANTENER: RESUMEN EJECUTIVO (esta parte sigue igual)
        reporte += f"\n\n💡 **RESUMEN EJECUTIVO:**"
        reporte += f"\n• Total elementos: {estadisticas['total_carpetas'] + estadisticas['total_archivos']:,}"
        reporte += f"\n• Carpetas: {estadisticas['total_carpetas']:,}"
        reporte += f"\n• Archivos: {estadisticas['total_archivos']:,}"

        if buscar_nombre:
            # Contar por tipo usando la nueva estructura
            carpetas_encontradas = sum(1 for c in estadisticas['coincidencias'] if 'carpeta' in c['tipo'])
            archivos_encontrados = sum(1 for c in estadisticas['coincidencias'] if 'archivo' in c['tipo'])

            if carpetas_encontradas + archivos_encontrados > 0:
                reporte += f"\n• ✅ '{buscar_nombre}' encontrado: SÍ ({carpetas_encontradas} carpetas, {archivos_encontrados} archivos)"
            else:
                reporte += f"\n• ❌ '{buscar_nombre}' encontrado: NO"

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
            "carpeta": '📁'
        }
        return iconos.get(extension, '📄')