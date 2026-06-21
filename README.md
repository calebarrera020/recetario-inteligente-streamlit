# Recetario Inteligente

Proyecto en Python para guardar recetas de cocina con imagenes, buscador, sugerencias basadas en ingredientes disponibles y modo claro/oscuro.

## Funciones incluidas

- Guardar recetas con nombre, descripcion, categoria, dificultad, tiempo y porciones.
- Registrar ingredientes por separado con cantidad.
- Agregar pasos de preparacion en orden vertical.
- Adjuntar una o varias fotos de referencia por receta.
- Buscar recetas por nombre o por ingredientes.
- Cambiar entre modo claro y modo oscuro.
- Interfaz adaptable para celular y escritorio.
- Portada con favoritas y recetas guardadas recientes.
- Estilo visual lila en modo claro y oscuro.
- Ver sugerencias de recetas segun los ingredientes que tienes en tu cocina.
- Editar o eliminar recetas ya guardadas.
- Marcar recetas favoritas.
- Preparado para publicarse en Streamlit Community Cloud.
- Compatible con SQLite local y Neon Postgres para datos permanentes.

## Como ejecutarlo

1. Instala las dependencias:

```bash
pip install -r requirements.txt
```

2. Inicia la aplicacion:

```bash
streamlit run app.py
```

3. Streamlit abrira la aplicacion en tu navegador.

## Guardado local y guardado permanente

- En tu PC, la app usa `SQLite` y guarda en `data/recipes.db`.
- En la nube, puedes usar `Neon Postgres` para que las recetas no se pierdan.
- Para usar Neon, configura `DATABASE_URL` como secreto de Streamlit Cloud.

## Verla desde otro movil

Si el otro movil no esta conectado a tu misma red Wi-Fi, necesitas publicar la app en internet.

Consulta:

- `DEPLOY.md`

## Estructura

- `app.py`: interfaz principal.
- `recipe_app/db.py`: creacion y conexion a la base de datos local o remota.
- `recipe_app/services.py`: logica para guardar, editar, buscar y recomendar recetas.
- `data/`: base de datos e imagenes cargadas.

## Ideas para una segunda version

- Lista de compras automatica.
- Plan semanal de comidas.
- Calificaciones por estrellas.
- Exportar recetas a PDF.
- Login por usuario.
