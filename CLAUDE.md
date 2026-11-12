# Canal de ciencia visual: reglas de trabajo

Shorts 9:16 (1080x1920, 30 fps, 30-60 s). Fondo azul noche, colores cian, naranja y amarillo. Máximo 8 palabras por escena. Escena nueva cada 3-5 s. Estructura: gancho con pregunta (0-3 s), pasos, dato sorprendente con fuente, pregunta final. Explicado para alguien de 14 años.

## Cómo crear un vídeo (camino corto)
1. Datos: buscar solo el dato sorprendente y las cifras dudosas (1-3 búsquedas). Anotar fuente en `facts.md`.
2. Guion: lista `SCENES` en `videos/<slug>.py` (dur, texto, índices resaltados, color, función[, y del titular]).
3. Escenas: reutilizar `lib/engine.py` (label, metal_rect, flow_dots, spark, fill_grad, glow_*) y `lib/render2.py` (draw_sat, draw_dish3d, draw_building, draw_reflector, draw_tv_real…). `lib/globe.py` para la Tierra.
4. Revisión: UNA hoja de contacto `python videos/<slug>.py sheet /tmp/s.png` (un fotograma al 80 % de cada escena). Leerla una vez, corregir todo junto, revisar solo las escenas cambiadas con `still`.
5. Render: `tools/render_local.sh <slug...>` (todos los núcleos) o push a GitHub (Actions renderiza en paralelo y publica en Releases).
6. Entrega: enviar los mp4 con un resumen corto. Sin repetir el guion.

## Ahorro de tokens
- No releer archivos ya leídos. Editar con Edit o con scripts python cortos, no reescribir archivos enteros.
- Imágenes de revisión pequeñas (hojas de 405x720 por escena), nunca fotogramas sueltos a tamaño completo salvo para un problema concreto.
- Agrupar llamadas a herramientas independientes en un solo mensaje.
- Mensajes al usuario breves: qué se entregó, datos con fuente y una siguiente opción.
- Reutilizar escenas tipo: gancho, piezas con etiquetas, ¡DATO!, comentarios (CTA).
