"""
Generador de documentos de ejemplo para Santos Pegasus Soluciones
Crea 5 PDFs con contenido realista para probar el pipeline RAG
"""
import os
from pathlib import Path
from fpdf import FPDF
from datetime import datetime

class PDFGenerator(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Santos Pegasus Soluciones', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Documento Interno - {datetime.now().year}', 0, 0, 'C')
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)
    
    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 7, body)
        self.ln()

def create_sample_documents():
    """Genera 5 documentos PDF de ejemplo"""
    docs_dir = Path("data/documentos")
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    documents = [
        {
            "filename": "manual_onboarding_devs.pdf",
            "title": "Manual de Onboarding para Nuevos Desarrolladores",
            "content": """
            Bienvenido al equipo de Santos Pegasus Soluciones. Este manual está diseñado para 
            ayudarte en tus primeros pasos dentro de la organización.
            
            Nuestra filosofía se basa en tres pilares fundamentales: excelencia técnica, 
            colaboración continua y enfoque en el cliente.
            
            Durante tu primera semana, completarás el proceso de integración que incluye:
            1. Configuración de tu entorno de desarrollo (IDE, repositorios, herramientas)
            2. Revisión de la arquitectura de microservicios de la empresa
            3. Sesiones de pairing con desarrolladores senior
            4. Acceso a la documentación técnica y repositorios internos
            
            Las herramientas principales que utilizarás incluyen: Python 3.11+, Docker, Kubernetes,
            GitHub Actions para CI/CD, y OCI (Oracle Cloud Infrastructure) para despliegues.
            
            Nuestros microservicios están organizados por dominios: usuarios, productos, pagos,
            notificaciones y analytics. Cada equipo es responsable de su propio ciclo de vida.
            
            La comunicación interna se maneja a través de Slack y el seguimiento de tareas en Jira.
            Realizamos daily standups a las 10:00 AM y sprints de dos semanas.
            
            Los principios de clean code y testing son obligatorios. Mantenemos una cobertura
            mínima del 85% en nuestras pruebas unitarias.
            """
        },
        {
            "filename": "guia_backend_engineering.pdf",
            "title": "Guía Oficial de Ingeniería Back-end",
            "content": """
            Guía de mejores prácticas para el desarrollo backend en Santos Pegasus Soluciones.
            
            Estándares de código Python:
            - Seguimos PEP 8 estrictamente con Black como formateador automático
            - Usamos type hints en todas las funciones para mejorar la mantenibilidad
            - Las docstrings son obligatorias para módulos, clases y funciones públicas
            - Las excepciones deben ser específicas y manejadas apropiadamente
            
            Arquitectura de microservicios:
            - Cada microservicio es un proyecto independiente con su propio repositorio
            - Comunicación síncrona vía REST APIs y gRPC para servicios críticos
            - Comunicación asíncrona usando RabbitMQ para eventos y colas
            - Usamos el patrón API Gateway para el enrutamiento y autenticación
            - Los servicios se registran en Consul para service discovery
            
            Bases de datos:
            - PostgreSQL para datos transaccionales con migraciones usando Alembic
            - Redis para caché y sesiones con TTL configurable
            - MongoDB para logs y datos no estructurados
            - Elasticsearch para búsquedas y análisis
            
            Seguridad:
            - Autenticación OAuth 2.0 + JWT
            - Cifrado de datos sensibles en reposo y en tránsito
            - Rate limiting por endpoint para prevenir ataques
            - Auditoría de accesos y acciones críticas
            
            CI/CD Pipeline:
            - Cada PR ejecuta tests automáticos y linting
            - Despliegue en desarrollo a través de GitHub Actions
            - Aprobación manual para despliegue a producción
            - Monitoreo con Prometheus y Grafana
            """
        },
        {
            "filename": "guia_frontend_engineering.pdf",
            "title": "Guía Oficial de Ingeniería Front-end",
            "content": """
            Guía de desarrollo frontend para Santos Pegasus Soluciones.
            
            Stack tecnológico:
            - React 18+ con TypeScript para aplicaciones web
            - Next.js para SSR y optimización de rendimiento
            - Tailwind CSS para estilizado y diseño responsivo
            - React Query para manejo de estado y caché de datos
            - Zustand para estado global cuando sea necesario
            
            Componentes y arquitectura:
            - Utilizamos el patrón Atomic Design para organizar componentes
            - Los componentes deben ser reutilizables y con prop-types tipados
            - Hooks personalizados para lógica de negocio reutilizable
            - Lazy loading para optimizar la carga inicial
            
            Accesibilidad (a11y):
            - Cumplimos con WCAG 2.1 nivel AA
            - Uso de ARIA labels y roles apropiados
            - Pruebas de contraste de color y navegación por teclado
            - Texto alternativo en todas las imágenes
            
            Rendimiento:
            - Métricas core: LCP < 2.5s, FID < 100ms, CLS < 0.1
            - Optimización de imágenes con next/image
            - Code splitting y bundle optimization
            - Service Workers para funcionalidad offline
            
            Testing:
            - Jest + React Testing Library para pruebas unitarias
            - Cypress para pruebas end-to-end
            - Storybook para desarrollo y documentación de componentes
            - Cobertura mínima del 80%
            """
        },
        {
            "filename": "protocolo_incidentes.pdf",
            "title": "Protocolo de Respuesta a Incidentes y Post-Mortems",
            "content": """
            Protocolo oficial para manejo de incidentes en Santos Pegasus Soluciones.
            
            Clasificación de incidentes:
            - Severidad 1: Servicio crítico caído, afectación a clientes
            - Severidad 2: Degradación de servicio, funcionalidad parcial
            - Severidad 3: Problemas menores, sin impacto en clientes
            - Severidad 4: Incidentes programados o no críticos
            
            Timeline de respuesta:
            0-5 minutos: Alerta y reconocimiento del incidente
            5-15 minutos: Evaluación inicial y clasificación
            15-30 minutos: Análisis de causa raíz (RCA)
            30-60 minutos: Implementación de solución temporal
            60-120 minutos: Corrección definitiva y validación
            
            Canales de comunicación:
            - #incidentes-urgentes para comunicación inmediata (Slack)
            - Bridge de llamada para coordinación en vivo
            - Actualizaciones cada 15 minutos a stakeholders
            - Comunicación a clientes según severidad
            
            Post-Mortem:
            - Se realiza dentro de las 48 horas posteriores
            - Participan todos los involucrados en la resolución
            - Documentación detallada de qué pasó, por qué y cómo se resolvió
            - Plan de acción para prevenir recurrencias
            
            Métricas de seguimiento:
            - MTTR (Mean Time To Resolution)
            - MTBF (Mean Time Between Failures)
            - Número de incidentes por mes
            - Satisfacción del cliente post-incidente
            """
        },
        {
            "filename": "arquitectura_microservicios.pdf",
            "title": "Arquitectura de Microservicios y Mapa de Dominios",
            "content": """
            Documento de arquitectura de microservicios de Santos Pegasus Soluciones.
            
            Estrategia de microservicios:
            - Separación por dominio de negocio (Domain-Driven Design)
            - Cada servicio tiene su propia base de datos (Database per Service)
            - Comunicación asíncrona mediante eventos para evitar acoplamiento
            - Despliegue independiente y escalado horizontal
            
            Dominios principales:
            1. Servicio de Usuarios: Gestión de perfiles, autenticación, roles
            2. Servicio de Productos: Catálogo, inventario, precios
            3. Servicio de Pagos: Procesamiento, facturación, suscripciones
            4. Servicio de Notificaciones: Email, SMS, push notifications
            5. Servicio de Analytics: Reportes, métricas, dashboards
            
            Patrones implementados:
            - Saga para transacciones distribuidas
            - Circuit Breaker para tolerancia a fallos (Resilience4j)
            - CQRS para separación de lectura/escritura
            - Event Sourcing para auditoría histórica
            
            Infraestructura:
            - Kubernetes en OCI para orquestación
            - Istio para service mesh y observabilidad
            - OCI Object Storage para almacenamiento de archivos
            - OCI Streaming para procesamiento de eventos en tiempo real
            
            Monitoreo y observabilidad:
            - Prometheus para métricas y alertas
            - Grafana para dashboards de visualización
            - ELK Stack para logs centralizados
            - Jaeger para distributed tracing
            """
        }
    ]
    
    for doc in documents:
        pdf = PDFGenerator()
        pdf.add_page()
        pdf.chapter_title(doc["title"])
        pdf.chapter_body(doc["content"].strip())
        
        # Añadir metadatos
        pdf.set_font('Arial', 'I', 9)
        pdf.cell(0, 5, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
        pdf.cell(0, 5, "Clasificación: Uso Interno", 0, 1)
        
        filepath = docs_dir / doc["filename"]
        pdf.output(str(filepath))
        print(f"✅ Documento generado: {filepath}")
    
    print("\n🎉 Todos los documentos generados correctamente!")

if __name__ == "__main__":
    create_sample_documents()