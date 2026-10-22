# Mejoras pendientes · llm-injection-case

Este caso se mejora poco a poco, en sesiones cortas: cada sesión coge el punto
más alto de la lista que esté sin hacer, lo implementa con resultados reales,
lo documenta y lo sube. Nada de inventar.

## Reglas del proyecto

- Resultados reales siempre. Si un experimento falla, se documenta lo observado; no se maquilla.
- `resultados/` es evidencia: no se edita a posteriori. Las ejecuciones nuevas se añaden sin borrar las anteriores.
- Los prompts de v1/v2, la frase marcador y los documentos no se tocan sin reejecutar la batería completa después.
- Textos de usuario en español.

## Contexto operativo

- Proyecto: carpeta `llm-injection-case/` del workspace de AutoClaw.
- Python: usar `C:\Python315\python.exe` (el `python` del PATH dentro de AutoClaw no resuelve los módulos locales).
- Ollama: si no responde en `http://localhost:11434`, arrancarlo con `Start-Process ollama -ArgumentList serve`.
  Modelos disponibles: `dolphin3:latest`, `gpt-oss:20b`, `qwen3:1.7b`, entre otros.
- Batería completa (¡`--limpiar` vacía el registro!; sin `--limpiar` añade casos sin borrar):
  `& C:\Python315\python.exe pruebas.py --version ambas`
- Añadir la batería con otro modelo: `& C:\Python315\python.exe pruebas.py --version v1 --modelo gpt-oss:20b`
- Resumen comparativo: `& C:\Python315\python.exe pruebas.py --resumen`
- Control de tokens (diagnóstico, no batería): `& C:\Python315\python.exe diagnostico_presupuesto.py --presupuesto 1500`
- GitHub: https://github.com/REDH0C/llm-injection-case — commit y push directos (credenciales ya autorizadas en el equipo).

## Backlog (por prioridad)

1. [x] **v2 con `gpt-oss:20b`** — ¿basta la separación + restricción con un modelo más alineado? Ejecutar la batería v2 con ese modelo y comparar contra dolphin3.
   *Hecho el 2026-10-22:* 11 casos nuevos (44 en total). Adversarias 0/6 con marcador y 0 neutralizadas: el modelo no generó el contenido inyectado, así que el cortafuegos no llegó a actuar. Con dolphin3, las mismas capas 1-2 no bastaron (6/6 generó el marcador). Ojo: con `num_predict: 400`, 4/6 respuestas de gpt-oss salieron cortadas (una vacía); el control con 1.500 tokens las completa y sigue 0/6. Evidencia en `resultados/2026-10-22_v2-gpt-oss-20b.md`.
2. [ ] **Evasión contra el cortafuegos** — paráfrasis del marcador, payload en inglés, instrucciones que ataquen los delimitadores. Documentar qué pasa y qué se cuela.
3. [ ] **README en inglés** — mantener el español como `README.es.md` y dejar `README.md` en inglés.
4. [ ] **Estabilidad de resultados** — repetir las baterías (n=3) y documentar la variabilidad entre ejecuciones.
5. [ ] **GitHub Actions básico** — workflow que verifique que los módulos compilan y que los CSV/JSON están bien formados.
6. [ ] **Segundo caso (agéntico)** — asistente con una herramienta real y payload que intente provocar una acción indebida; permisos de herramientas, aprobación humana y registro de acciones (marco OWASP para agentes).
7. [ ] **Automatización con PyRIT** — evaluar si aporta frente a la batería actual.
8. [ ] **Presupuesto de tokens con modelos que razonan** — `num_predict: 400` corta las respuestas de gpt-oss:20b (4/6 en v2; el razonamiento consume el presupuesto). Decidir si subir el límite o desactivar el razonamiento, y guardar `done_reason` en la batería para detectar cortes en vez de descubrirlos después.
