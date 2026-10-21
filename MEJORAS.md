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
- GitHub: https://github.com/REDH0C/llm-injection-case — commit y push directos (credenciales ya autorizadas en el equipo).

## Backlog (por prioridad)

1. [ ] **v2 con `gpt-oss:20b`** — ¿basta la separación + restricción con un modelo más alineado? Ejecutar la batería v2 con ese modelo y comparar contra dolphin3.
2. [ ] **Evasión contra el cortafuegos** — paráfrasis del marcador, payload en inglés, instrucciones que ataquen los delimitadores. Documentar qué pasa y qué se cuela.
3. [ ] **README en inglés** — mantener el español como `README.es.md` y dejar `README.md` en inglés.
4. [ ] **Estabilidad de resultados** — repetir las baterías (n=3) y documentar la variabilidad entre ejecuciones.
5. [ ] **GitHub Actions básico** — workflow que verifique que los módulos compilan y que los CSV/JSON están bien formados.
6. [ ] **Segundo caso (agéntico)** — asistente con una herramienta real y payload que intente provocar una acción indebida; permisos de herramientas, aprobación humana y registro de acciones (marco OWASP para agentes).
7. [ ] **Automatización con PyRIT** — evaluar si aporta frente a la batería actual.
