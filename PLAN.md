# Plan de optimización: 60 ideas, del encargo a la entrega

Leyenda: ✅ ya aplicado · 🔜 se aplica en el siguiente vídeo · 💡 opcional

## 1. Encargo y guion
1. ✅ Reglas del canal guardadas en `CLAUDE.md`: no hay que repetirlas en cada pedido.
2. 🔜 Pedidos en una línea: "tema + nada más". El resto ya está definido.
3. 🔜 Varios vídeos por pedido: comparten búsqueda, revisión y render en un solo lote.
4. 🔜 Estructura fija de 11-13 escenas: gancho, 7-9 pasos, dato, pregunta final.
5. 🔜 Guion escrito directamente como lista `SCENES`, sin borrador previo en el chat.
6. 🔜 Titulares de ≤8 palabras ya contados al escribirlos, no corregidos después.
7. 💡 Banco de ganchos y preguntas finales reutilizables por tema.
8. 🔜 Duración objetivo de 45-50 s: deja margen y no hay que recortar escenas.

## 2. Datos y fuentes
9. 🔜 Buscar solo el dato sorprendente y las cifras dudosas (1-3 búsquedas, no 4+).
10. 🔜 Búsqueda en modo estándar; el modo extendido solo si falla.
11. 🔜 Archivo `facts.md` con datos ya verificados y su fuente, reutilizable.
12. 🔜 Preferir fuentes primarias (agencias, fabricantes, universidades) a la primera.
13. 🔜 Sin datos numéricos que no se puedan citar: frases cualitativas en su lugar.
14. 💡 Lote de datos para 5-10 temas futuros en una sola sesión de búsqueda.

## 3. Código y librería visual
15. ✅ Motor común `lib/engine.py`: fondo, titulares animados, transiciones y render.
16. ✅ Piezas realistas reutilizables: Tierra 3D, satélite, antena, metal, cobre, latón, chispas, flujos.
17. ✅ Cada vídeo es un archivo pequeño en `videos/` que solo define escenas.
18. 🔜 Plantillas de escena: "¡DATO!", "pregunta final" y "piezas con etiquetas" como funciones con parámetros.
19. 🔜 Componentes mecánicos genéricos: pistón, engranaje, muelle, eje, válvula, cable, pila y tubo.
20. 🔜 Diagramas en corte con capas: carcasa, interior y flujo de color, configurables.
21. 🔜 Etiquetas con posición automática para que no se pisen.
22. 🔜 Paletas fijas por material (acero, cobre, latón, plástico, fuego, agua).
23. 💡 Formato de guion en JSON/YAML para vídeos sencillos, sin escribir Python.
24. ✅ Rutas de recursos absolutas: funciona igual en local y en la nube.
25. ✅ Textura de la Tierra cacheada (`assets/cache`), se genera una sola vez.
26. 🔜 Ediciones con scripts de reemplazo cortos, nunca reescribiendo archivos enteros.

## 4. Revisión de calidad
27. ✅ Hoja de contacto: un fotograma por escena en una sola imagen (modo `sheet`).
28. 🔜 Una sola ronda de revisión: anotar todos los fallos y corregirlos juntos.
29. 🔜 Volver a mirar solo las escenas tocadas (modo `still`), no la hoja entera.
30. 🔜 Hoja a baja resolución (405x720 por escena): suficiente para ver solapes.
31. 💡 Comprobación automática de texto fuera de pantalla y etiquetas solapadas.
32. 💡 Contador automático de palabras por titular (aviso si pasa de 8).
33. 🔜 Revisar el vídeo final con 8 fotogramas muestreados, no reproduciéndolo.
34. 🔜 Margen seguro de Shorts: nada importante en los 300 px inferiores ni en el borde derecho.

## 5. Render
35. ✅ Una escena = un archivo de vídeo; unión sin recodificar (`-c copy`).
36. ✅ Fotogramas en memoria directos a ffmpeg (sin PNG intermedios).
37. ✅ Modo `all`: todas las escenas a la vez usando todos los núcleos.
38. ✅ Escenas más largas primero para repartir mejor la carga.
39. ✅ GitHub Actions: una máquina cada 2 escenas, hasta 20 a la vez.
40. ✅ Unión y publicación automática en Releases al terminar.
41. ✅ Render automático al hacer push de un vídeo nuevo o modificado.
42. ✅ Si cambia la librería común, se re-renderizan todos los vídeos.
43. ✅ Caché de pip y de la textura en Actions: arranque más rápido.
44. ✅ `fail-fast: false`: si falla una escena, el resto sigue y se reintenta solo esa.
45. 🔜 Re-render parcial: solo las escenas cambiadas (`scenes <dir> 3 7`) + unión.
46. ✅ H.264 `veryfast` CRF 18: calidad alta, codificación rápida.
47. 💡 Escenas idénticas entre vídeos (pregunta final) renderizadas una vez y reutilizadas.
48. 💡 Ajustar escenas por máquina (`per_job`) según la longitud del lote.
49. 💡 Repositorio público: minutos de Actions ilimitados y gratis.

## 6. Entrega
50. ✅ Vídeos listos en Releases: descarga directa desde el móvil.
51. 🔜 Entrega en un solo mensaje con todos los vídeos del lote.
52. 🔜 Resumen corto: datos con fuente y una siguiente opción, sin repetir el guion.
53. 💡 Texto de título, descripción y hashtags generado junto al vídeo.
54. 💡 Miniatura (primer fotograma del gancho) exportada automáticamente.
55. 💡 Pista de música/efectos añadida con `-c:v copy` sin volver a renderizar.

## 7. Ahorro de tokens
56. 🔜 No releer archivos ya leídos ni mostrar salidas largas de comandos (`| tail`, `| head`).
57. 🔜 Agrupar herramientas independientes en un mismo paso.
58. 🔜 Menos narración intermedia: solo avisos cuando algo cambia lo que recibirás.
59. 🔜 Reutilizar funciones de la librería en vez de dibujar desde cero cada vez.
60. 🔜 Revisiones visuales pequeñas y una sola por vídeo.
61. 🔜 Render pesado fuera de la sesión (GitHub): la sesión solo escribe código y entrega.
62. 💡 Pedidos por lotes de 4-5 temas: el contexto común se carga una vez.
