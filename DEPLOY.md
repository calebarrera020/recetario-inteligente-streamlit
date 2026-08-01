# Publicar Recetario Inteligente

Si quieres abrir esta app desde otro movil que no este conectado a tu misma red Wi-Fi, necesitas publicarla en internet.

## Opcion recomendada

Usa `GitHub + Streamlit Community Cloud + Neon Postgres`.

## Paso 1. Crear la base de datos en Neon

1. Crea una cuenta en Neon.
2. Crea un proyecto nuevo.
3. Copia la cadena de conexion.
4. Si Neon te la da empezando con `postgresql://`, cambiala para que empiece con `postgresql+psycopg://`.
5. Esa cadena se usara como `DATABASE_URL`.

## Paso 2. Subir el proyecto a GitHub

1. Crea un repositorio nuevo.
2. Sube esta carpeta completa.
3. Verifica que `requirements.txt`, `runtime.txt`, `app.py` y la carpeta `.streamlit` queden en la raiz.
4. No subas `.streamlit/secrets.toml`; solo deja `secrets.example.toml` como referencia.

## Paso 3. Publicar en Streamlit Community Cloud

1. Entra a Streamlit Community Cloud.
2. Elige `New app`.
3. Selecciona tu repositorio.
4. Indica que el archivo principal es `app.py`.
5. En `Advanced settings` agrega este secreto:

```toml
DATABASE_URL = "postgresql+psycopg://usuario:password@host/dbname?sslmode=require"
```

6. Pulsa `Deploy`.
7. Cuando abra, crea o edita una receta para confirmar que la base remota esta guardando datos.

## Paso 4. Poner la app en privado

1. Abre tu app en Streamlit Cloud.
2. Entra a `Settings`.
3. Ve a la seccion `Sharing`.
4. En `Who can view this app`, elige `Only specific people can view this app`.
5. Agrega el correo de tu pareja como persona autorizada.
6. Ella podra entrar desde cualquier celular o red, pero tendra que abrir el enlace e iniciar sesion con ese correo.

## Resultado

Streamlit te entregara una URL privada similar a:

```text
https://tu-app.streamlit.app
```

Esa direccion se puede abrir desde cualquier movil con internet, y como la app estara en privado solo las personas autorizadas podran entrar.

## Nota importante sobre las fotos

Las fotos de las recetas ya quedan guardadas dentro de la base de datos. Eso ayuda a que sigan visibles en Streamlit Cloud incluso despues de reinicios o nuevas publicaciones.
