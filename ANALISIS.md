# 📊 Resultados de Análisis: Tiempos de Respuesta vs Modelos LLM

Este documento permite registrar y analizar la latencia (tiempo de respuesta en segundos) obtenida con la aplicación `mi_chat_llm` conectada a Ollama local (`http://localhost:11434/api/generate`).

---

## 🧪 Tabla Comparativa de Rendimiento

| ID | Prompt / Pregunta de Prueba (Asignada) | Modelo: `gemma2:2b` (sec) | Modelo: `llama3.2:3b` (sec) | Modelo: `llama3.1:8b` (sec) |
|---|---|---|---|---|
| 1 | **P. Simple:** "Explica qué es un algoritmo en 2 oraciones." | 14.14 | 18.19 | 35.70 |
| 2 | **P. Medio:** "Escribe una función en Python para invertir una cadena de texto." | 87.83 | 112.27 | 107.67 |
| 3 | **P. Específico:** "Cuáles son las 3 leyes de la termodinámica?" | 17.37 | 42.44 | 22.51 |
| 4 | **P. Complejo:** (Prueba de carga lógica / contextual) | 88.39 | 113.50 | *SUPERÓ LÍMITE DE ESPERA* |

---

## 📈 Visualizaciones de Rendimiento

### 1. Tiempo de Respuesta por Tipo de Prompt
Esta gráfica muestra cómo reacciona cada modelo frente a la complejidad del prompt. 

![Gráfica de Barras - Tiempos](barras_tiempo.png)

### 2. Relación: Parámetros vs Latencia
La gráfica de dispersión evalúa si la relación entre el número de parámetros del modelo (2B, 3B, 8B) y su tiempo promedio de respuesta tiene un comportamiento lineal.

![Gráfica de Dispersión - Parámetros](dispersion_parametros.png)

---

## 📝 Observaciones y Conclusiones

- **`gemma2:2b`**: Presentó el mejor rendimiento general en tiempo de respuesta. Dado su tamaño reducido (2B), es el modelo más ágil, demostrando una excelente eficiencia para automatizaciones locales sin castigar en exceso la latencia, incluso en prompts complejos (~88s).
- **`llama3.2:3b`**: Tiene un desempeño curioso; a pesar de ser más ligero que el modelo de 8B, presentó los picos de latencia más altos en los prompts Medio y Complejo (superando los 112s). Esto impacta su promedio, ubicándolo por encima de la tendencia esperada.
- **`llama3.1:8b`**: El modelo más pesado tiene un comportamiento inconsistente en este hardware. Respondió razonablemente bien en tareas de nivel Específico y Medio, pero no logró completar la inferencia del prompt Complejo (TimeOut). 
- **Conclusión de la relación lineal**: La gráfica de dispersión muestra que **la relación no es estrictamente lineal**. Aunque hay una tendencia de crecimiento en el tiempo base (evaluando los prompts simples), el modelo de 3B genera un pico de latencia promedio que rompe la linealidad, y el modelo de 8B tiene el problema añadido de superar los límites de espera, lo que distorsiona su promedio efectivo.
