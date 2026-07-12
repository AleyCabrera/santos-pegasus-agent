"""Plantillas de prompts para el agente RAG"""

from langchain.prompts import PromptTemplate

# Prompt principal para el sistema RAG
RAG_PROMPT_TEMPLATE = """Eres un asistente virtual experto de "Santos Pegasus Soluciones", una empresa de tecnología especializada en inteligencia artificial y transformación digital.

Tu función es responder preguntas basándote EXCLUSIVAMENTE en el contexto proporcionado. 
Si la respuesta no está en el contexto, di claramente que no tienes esa información.

### Contexto:
{context}

### Pregunta del usuario:
{question}

### Instrucciones importantes:
1. Responde de manera clara, concisa y profesional
2. Usa el contexto proporcionado como única fuente de información
3. Si no encuentras la respuesta en el contexto, di: "No tengo información sobre eso en la documentación disponible"
4. Si el contexto contiene información parcial, responde con lo que tienes y menciona que podría haber más detalles
5. Mantén un tono amable y útil

### Respuesta:
"""

# Prompt para resumen de conversación
SUMMARY_PROMPT_TEMPLATE = """Resume la siguiente conversación de manera concisa:

Historial:
{history}

Resumen:
"""

# Prompt para clasificación de preguntas
CLASSIFICATION_PROMPT = """Clasifica la siguiente pregunta en una de estas categorías:
- onboarding: Preguntas sobre incorporación de nuevos empleados
- backend: Preguntas sobre ingeniería backend
- frontend: Preguntas sobre ingeniería frontend
- incidentes: Preguntas sobre protocolos de incidentes
- arquitectura: Preguntas sobre arquitectura de microservicios
- general: Preguntas generales que no encajan en las anteriores

Pregunta: {question}

Categoría (solo el nombre de la categoría):
"""

# Prompt para respuesta cuando no hay contexto
NO_CONTEXT_PROMPT = """No tengo información específica sobre esa pregunta en la documentación actual.

Pregunta: {question}

Por favor, consulta la documentación oficial o contacta al equipo correspondiente para obtener más información.

¿Hay algo más en lo que pueda ayudarte?
"""

# Crear objetos PromptTemplate
rag_prompt = PromptTemplate(
    template=RAG_PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)

summary_prompt = PromptTemplate(
    template=SUMMARY_PROMPT_TEMPLATE,
    input_variables=["history"]
)

classification_prompt = PromptTemplate(
    template=CLASSIFICATION_PROMPT,
    input_variables=["question"]
)

no_context_prompt = PromptTemplate(
    template=NO_CONTEXT_PROMPT,
    input_variables=["question"]
)