import psutil
import time
import platform
import subprocess


class MonitorRendimiento:
    """Módulo especializado en obtener métricas de rendimiento del sistema"""

    def __init__(self):
        self.ultimas_metricas = {}
        self.sistema_operativo = platform.system()

    def obtener_metricas_completas(self):
        """Obtiene métricas completas del sistema y las muestra en terminal"""
        try:
            print("📊 Iniciando análisis de rendimiento del sistema...")

            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # Memoria
            memoria = psutil.virtual_memory()
            memoria_percent = memoria.percent
            memoria_used_gb = memoria.used / (1024 ** 3)
            memoria_total_gb = memoria.total / (1024 ** 3)

            # Procesos
            procesos = len(psutil.pids())

            # Disco
            disco = psutil.disk_usage('/')
            disco_percent = disco.percent
            disco_used_gb = disco.used / (1024 ** 3)
            disco_total_gb = disco.total / (1024 ** 3)

            # Tiempo de actividad
            tiempo_actividad = time.time() - psutil.boot_time()
            horas = int(tiempo_actividad // 3600)
            minutos = int((tiempo_actividad % 3600) // 60)

            # Red (bytes enviados/recibidos)
            red = psutil.net_io_counters()
            red_sent_mb = red.bytes_sent / (1024 ** 2)
            red_recv_mb = red.bytes_recv / (1024 ** 2)

            # Temperatura - MEJORADO para diferentes sistemas
            temperatura = self._obtener_temperatura_mejorada()

            # Procesos que más consumen
            procesos_top = self._obtener_procesos_top()

            # Información adicional del sistema
            info_sistema = self._obtener_info_sistema()

            metricas = {
                "cpu": f"{cpu_percent}%",
                "memoria": f"{memoria_percent}% ({memoria_used_gb:.1f}GB/{memoria_total_gb:.1f}GB)",
                "procesos": f"{procesos}",
                "disco": f"{disco_percent}% ({disco_used_gb:.1f}GB/{disco_total_gb:.1f}GB)",
                "temperatura": temperatura,
                "tiempo_actividad": f"{horas}h {minutos}m",
                "red": f"▲ {red_sent_mb:.1f}MB ▼ {red_recv_mb:.1f}MB",
                "procesos_top": procesos_top,
                "info_sistema": info_sistema,
                "cpu_detalle": f"{cpu_percent}%",  # Para uso directo en IA
                "memoria_detalle": f"{memoria_percent}%",  # Para uso directo en IA
                "disco_detalle": f"{disco_percent}%"  # Para uso directo en IA
            }

            self.ultimas_metricas = metricas

            # Mostrar en terminal
            self._mostrar_metricas_terminal(metricas)

            return metricas

        except Exception as e:
            print(f"❌ Error obteniendo métricas: {e}")
            return self._metricas_error()

    def _obtener_temperatura_mejorada(self):
        """Obtiene la temperatura del sistema con métodos mejorados"""
        try:
            # Método 1: psutil estándar
            temps = psutil.sensors_temperatures()
            if temps:
                for nombre, valores in temps.items():
                    if valores and valores[0].current:
                        temp_actual = valores[0].current
                        return f"{temp_actual}°C"

            # Método 2: Para Windows - intentar con WMI
            if self.sistema_operativo == "Windows":
                return self._obtener_temperatura_windows()

            # Método 3: Para Linux
            elif self.sistema_operativo == "Linux":
                return self._obtener_temperatura_linux()

            return "Sensor no disponible"

        except Exception as e:
            print(f"⚠️ No se pudo obtener temperatura: {e}")
            return "No disponible"

    def _obtener_temperatura_windows(self):
        """Intenta obtener temperatura en Windows usando diferentes métodos"""
        try:
            # Método 1: Usando WMI (requiere pywin32)
            try:
                import wmi
                w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                sensors = w.Sensor()
                for sensor in sensors:
                    if sensor.SensorType == u'Temperature' and 'CPU' in sensor.Name:
                        return f"{sensor.Value}°C"
            except ImportError:
                pass

            # Método 2: Usando PowerShell para CPU
            try:
                result = subprocess.run([
                    'powershell',
                    'Get-WmiObject -Namespace "root\\WMI" -Class MSAcpi_ThermalZoneTemperature | Select-Object -ExpandProperty CurrentTemperature'
                ], capture_output=True, text=True, timeout=5)

                if result.returncode == 0 and result.stdout.strip():
                    temp_kelvin = int(result.stdout.strip()) / 10.0
                    temp_celsius = temp_kelvin - 273.15
                    return f"{temp_celsius:.1f}°C"
            except:
                pass

            return "Sensor no disponible en Windows"

        except Exception as e:
            return f"No disponible: {str(e)}"

    def _obtener_temperatura_linux(self):
        """Intenta obtener temperatura en Linux"""
        try:
            # Intentar leer de /sys/class/thermal
            import glob
            thermal_zones = glob.glob('/sys/class/thermal/thermal_zone*/temp')
            if thermal_zones:
                with open(thermal_zones[0], 'r') as f:
                    temp_millic = int(f.read().strip())
                    temp_celsius = temp_millic / 1000.0
                    return f"{temp_celsius:.1f}°C"
            return "Sensor no disponible en Linux"
        except:
            return "No disponible en Linux"

    def _obtener_info_sistema(self):
        """Obtiene información adicional del sistema"""
        try:
            info = {
                "sistema": platform.system(),
                "procesador": platform.processor(),
                "arquitectura": platform.architecture()[0],
                "nucleos_logicos": psutil.cpu_count(logical=True),
                "nucleos_fisicos": psutil.cpu_count(logical=False)
            }
            return info
        except:
            return {"sistema": "Desconocido"}

    def _obtener_procesos_top(self, cantidad=5):
        """Obtiene los procesos que más consumen recursos"""
        try:
            procesos = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    procesos.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Ordenar por uso de CPU
            procesos.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            top_procesos = procesos[:cantidad]

            # Formatear resultado
            resultado = []
            for proc in top_procesos:
                if proc['cpu_percent'] and proc['cpu_percent'] > 0:
                    resultado.append(f"{proc['name']}: CPU {proc['cpu_percent']:.1f}%")

            return resultado[:3] if resultado else ["Sin procesos destacados"]
        except:
            return ["Error obteniendo procesos"]

    def _mostrar_metricas_terminal(self, metricas):
        """Muestra las métricas de forma organizada en la terminal"""
        print("\n" + "=" * 60)
        print("📊 MÉTRICAS DE RENDIMIENTO - TIEMPO REAL")
        print("=" * 60)
        print(f"🖥️  CPU: {metricas['cpu']}")
        print(f"🧠 Memoria RAM: {metricas['memoria']}")
        print(f"🔄 Procesos activos: {metricas['procesos']}")
        print(f"💾 Disco: {metricas['disco']}")
        print(f"🌡️  Temperatura: {metricas['temperatura']}")
        print(f"⏰ Tiempo actividad: {metricas['tiempo_actividad']}")
        print(f"📡 Red: {metricas['red']}")

        # Información del sistema
        info = metricas['info_sistema']
        print(f"💻 Sistema: {info.get('sistema', 'Desconocido')} - {info.get('arquitectura', '?')}")
        print(f"🔢 Núcleos: {info.get('nucleos_fisicos', '?')} físicos, {info.get('nucleos_logicos', '?')} lógicos")

        if metricas['procesos_top']:
            print(f"🔥 Procesos top: {', '.join(metricas['procesos_top'])}")

        # Análisis de estado
        self._analizar_estado_sistema(metricas)
        print("=" * 60 + "\n")

    def _analizar_estado_sistema(self, metricas):
        """Analiza el estado del sistema y muestra alertas si es necesario"""
        alertas = []

        # Analizar CPU
        try:
            cpu_valor = float(metricas['cpu_detalle'].replace('%', ''))
            if cpu_valor > 80:
                alertas.append("🚨 CPU muy alta - Considera cerrar aplicaciones")
            elif cpu_valor > 60:
                alertas.append("⚠️  CPU moderada - Monitorea el uso")
        except:
            pass

        # Analizar Memoria
        try:
            mem_valor = float(metricas['memoria_detalle'].replace('%', ''))
            if mem_valor > 85:
                alertas.append("🚨 Memoria crítica - Puede haber ralentización")
            elif mem_valor > 70:
                alertas.append("⚠️  Memoria alta - Considera liberar espacio")
        except:
            pass

        # Analizar Disco
        try:
            disco_valor = float(metricas['disco_detalle'].replace('%', ''))
            if disco_valor > 90:
                alertas.append("🚨 Disco casi lleno - Libera espacio urgentemente")
            elif disco_valor > 80:
                alertas.append("⚠️  Disco alto - Considera limpiar archivos")
        except:
            pass

        if alertas:
            print("\n🔔 ALERTAS DEL SISTEMA:")
            for alerta in alertas:
                print(f"   • {alerta}")
        else:
            print("\n✅ Sistema funcionando correctamente")

    def _metricas_error(self):
        """Retorna métricas de error"""
        return {
            "cpu": "Error",
            "memoria": "Error",
            "procesos": "Error",
            "disco": "Error",
            "temperatura": "Error",
            "tiempo_actividad": "Error",
            "red": "Error",
            "procesos_top": ["Error"],
            "info_sistema": {"sistema": "Error"},
            "cpu_detalle": "Error",
            "memoria_detalle": "Error",
            "disco_detalle": "Error"
        }

    def obtener_resumen_rendimiento(self):
        """Retorna un resumen rápido del rendimiento"""
        if not self.ultimas_metricas:
            self.obtener_metricas_completas()

        metricas = self.ultimas_metricas
        return f"CPU: {metricas['cpu']} | Mem: {metricas['memoria'].split(' ')[0]} | Procs: {metricas['procesos']}"