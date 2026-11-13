# Canal: historias animadas en inglés (EE. UU.)

Formatos: "Stories With a Twist" y "Would You Survive?". Shorts 1080x1920 (30-60 s) y largos 1920x1080 (8-15 min).
Estilo: stickman original (`lib/stick.py`), fondos oscuros (`theme='noir'`), acento rojo/amarillo, subtítulos palabra a palabra en inglés (`caption`), cambio de plano cada 2-4 s, medidores (`heart_meter`, `speed_meter`).
Estructura: gancho 0-3 s, bucle abierto, escalada, giro final, corte seco (`fades=False`) o pregunta para comentar.
Narración: voz IA (ElevenLabs) más tarde; el guion va por escenas con duración. Al recibir el audio, re-sincronizar subtítulos con sus marcas de tiempo.
Contenido apto para monetizar: suspense sí, gore no. Hablar con el usuario en español; contenido del canal en inglés.

## Flujo
1. Guion por escenas (tabla: nº, duración, narración EN, subtítulo, animación). El usuario aprueba.
2. `videos/<slug>.py`: SCENES con texto vacío y `cap(...)` dentro de cada escena; `run(SCENES, theme='noir', fades=False)`.
3. Una hoja de revisión: `python videos/<slug>.py sheet /tmp/s.png`; corregir todo junto.
4. Push → GitHub Actions renderiza en paralelo y publica en Releases (render-N).
5. Paquete: 5 títulos (<60 car.), descripción con keywords, 10 hashtags, texto miniatura (≤4 palabras).

## Ahorro de tokens
No releer archivos; ediciones con scripts cortos; revisiones con hojas pequeñas; mensajes breves; reutilizar escenas e interiores.
`archive/ciencia/` contiene el proyecto anterior (no se renderiza).
