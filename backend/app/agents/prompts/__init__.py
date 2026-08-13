"""Prompt templates for the Meeting Intelligence Agent."""

SYSTEM_PROMPT = """Eres un asistente de inteligencia de reuniones. Tu trabajo es analizar transcripciones de reuniones y extraer información estructurada.

Reglas importantes:
- Solo detecta información que esté EXPLÍCITAMENTE mencionada en la transcripción.
- No inventes ni infiera información que no esté presente.
- Si no hay nada relevante que detectar, devuelve listas vacías.
- Responde siempre en el mismo idioma que la transcripción.
- Asigna un score de confianza (0.0 a 1.0) basado en qué tan explícita es la información.
"""

ACTION_ITEMS_PROMPT = """Analiza la siguiente transcripción de reunión y detecta ACTION ITEMS (tareas pendientes).

SOLO extrae action items que cumplan AL MENOS uno de estos criterios:
1. Tarea específica mencionada explícitamente ("hay que hacer X", "necesitamos X")
2. Persona asignada claramente ("Luis se encarga de...", "María va a...")
3. Deadline o timeframe mencionado ("para el viernes", "la semana que viene")

Para cada action item detectado, proporciona:
- task: descripción concreta de la tarea
- assignee: persona asignada (null si no se menciona)
- deadline: plazo mencionado (null si no se menciona)
- priority: "low", "medium" o "high" basado en urgencia/importancia mencionada
- confidence: 0.0 a 1.0 (qué tan seguro estás de que es un action item real)

TRANSCRIPCIÓN:
{transcript}

Responde en JSON con esta estructura exacta:
{{"action_items": [...]}}

Si no hay action items, responde: {{"action_items": []}}"""

DECISIONS_PROMPT = """Analiza la siguiente transcripción de reunión y detecta DECISIONES tomadas.

SOLO extrae decisiones que:
1. Se expresen de forma definitiva ("decidimos que...", "vamos a...", "ok, hacemos X")
2. Impliquen un cambio de dirección o elección entre opciones
3. Sean acordadas (no propuestas rechazadas ni ideas sin confirmar)

NO detectes:
- Propuestas que no fueron aceptadas
- Ideas mencionadas de pasada sin confirmación
- Opiniones individuales que no son decisiones del grupo

Para cada decisión detectada:
- decision: descripción de la decisión
- context: contexto breve de por qué se tomó (null si no es claro)
- impact: "low", "medium" o "high"
- decision_maker: quién tomó o propuso la decisión (null si no está claro)
- confidence: 0.0 a 1.0

TRANSCRIPCIÓN:
{transcript}

Responde en JSON con esta estructura exacta:
{{"decisions": [...]}}

Si no hay decisiones, responde: {{"decisions": []}}"""

RISKS_PROMPT = """Analiza la siguiente transcripción de reunión y detecta RIESGOS o preocupaciones mencionadas.

SOLO detecta riesgos que:
1. Se mencionen explícitamente como problema, preocupación u obstáculo
2. Impliquen impacto negativo potencial en el proyecto/equipo
3. No estén ya resueltos en la misma conversación

Tipos de riesgos:
- technical: problemas técnicos, deuda técnica, limitaciones
- timeline: retrasos, plazos apretados, dependencias de tiempo
- resource: falta de personal, presupuesto, herramientas
- dependency: dependencias externas, terceros, aprobaciones

Para cada riesgo detectado:
- description: descripción del riesgo
- category: "technical", "timeline", "resource" o "dependency"
- severity: "low", "medium", "high" o "critical"
- mitigation: mitigación sugerida si se mencionó (null si no)
- confidence: 0.0 a 1.0

TRANSCRIPCIÓN:
{transcript}

Responde en JSON con esta estructura exacta:
{{"risks": [...]}}

Si no hay riesgos, responde: {{"risks": []}}"""

QUESTIONS_PROMPT = """Analiza la siguiente transcripción de reunión y detecta PREGUNTAS ABIERTAS que quedaron sin respuesta.

SOLO detecta preguntas que:
1. Se formularon explícitamente durante la reunión
2. NO recibieron una respuesta satisfactoria en la misma conversación
3. Requieren seguimiento o investigación posterior

NO detectes:
- Preguntas retóricas
- Preguntas que fueron respondidas inmediatamente
- Preguntas de cortesía ("¿cómo estás?")

Para cada pregunta abierta:
- question: la pregunta tal como se formuló
- context: contexto de por qué se preguntó (null si no es claro)
- asked_by: quién la formuló (null si no es claro)
- assigned_to: a quién se le pidió investigar/responder (null si no es claro)
- confidence: 0.0 a 1.0

TRANSCRIPCIÓN:
{transcript}

Responde en JSON con esta estructura exacta:
{{"questions": [...]}}

Si no hay preguntas abiertas, responde: {{"questions": []}}"""

SUMMARY_PROMPT = """Genera un resumen ejecutivo de la siguiente reunión.

El resumen debe ser:
- Conciso pero completo (máximo 300 palabras)
- Estructurado con secciones claras
- Accionable (que alguien que no estuvo pueda entender qué pasó)
- En el mismo idioma que la transcripción

Estructura del resumen:
1. **Sinopsis**: 2-3 frases sobre de qué trató la reunión
2. **Puntos clave**: los temas principales discutidos (bullet points)
3. **Próximos pasos**: qué se espera que pase después

PARTICIPANTES: {participants}

TRANSCRIPCIÓN:
{transcript}

ACTION ITEMS DETECTADOS:
{action_items}

DECISIONES DETECTADAS:
{decisions}

Genera el resumen en formato markdown:"""
