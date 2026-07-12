# Crear archivo create_test_docs.py
from pathlib import Path

# Crear directorios si no existen
Path("data/pdfs").mkdir(parents=True, exist_ok=True)
Path("data/csv").mkdir(parents=True, exist_ok=True)

# Crear PDF de prueba (simulado como .txt)
test_content = """# MANUAL DE ONBOARDING - SANTOS PEGASUS SOLUCIONES

## Bienvenida
Bienvenido a Santos Pegasus Soluciones, empresa líder en soluciones de IA.

## Estructura Organizacional
- CEO: Dirección estratégica
- CTO: Liderazgo técnico
- Equipos: Backend, Frontend, DevOps, Data

## Políticas
- Horario flexible
- 22 días de vacaciones
- 3 días remoto / 2 días oficina

## Herramientas
- Slack para comunicación
- GitHub para código
- Jira para gestión

Este es el manual de onboarding para nuevos empleados.
"""

with open("data/pdfs/manual_onboarding.txt", "w", encoding="utf-8") as f:
    f.write(test_content)

# Crear CSV de incidentes
incidentes_content = """Severidad,Nivel,Descripcion,Tiempo_Respuesta,Accion_Immediata,Escalamiento
0,Critico,Sistema completo caído,15 minutos,Alertar a todos,CTO
1,Alto,Caída de servicio crítico,30 minutos,Formar equipo de incidentes,Head de Ingeniería
2,Medio,Funcionalidad degradada,1 hora,Diagnóstico y análisis,Team Lead
3,Bajo,Fallo en funcionalidad no crítica,4 horas,Documentar y priorizar,Desarrollador
4,Informativo,Incidente reportado,1 día,Registrar en sistema,Equipo de soporte
"""

with open("data/csv/incidentes.csv", "w", encoding="utf-8") as f:
    f.write(incidentes_content)

print("✅ Archivos de prueba creados!")