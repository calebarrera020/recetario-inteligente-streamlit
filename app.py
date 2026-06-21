from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from recipe_app.services import (
    RecipePayload,
    clean_ingredients,
    clean_steps,
    create_recipe,
    delete_recipe,
    get_all_known_ingredients,
    get_categories,
    get_dashboard_stats,
    get_pantry_suggestions,
    get_recipe,
    list_recipes,
    seed_sample_data,
    update_recipe,
)

st.set_page_config(
    page_title="Recetario Inteligente",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def apply_theme(theme_name: str) -> None:
    themes = {
        "Claro": {
            "bg": "#fffbfd",
            "bg_second": "#f7effa",
            "panel": "#fffdfd",
            "panel_alt": "#fcf6ff",
            "text": "#433255",
            "muted": "#8d7d9f",
            "accent": "#cfb0ec",
            "accent_soft": "#f4e9ff",
            "accent_strong": "#ad84d7",
            "border": "#eadcf7",
            "success": "#5c9c73",
            "sidebar": "rgba(255, 251, 253, 0.98)",
            "button_text": "#ffffff",
        },
        "Oscuro": {
            "bg": "#2a213a",
            "bg_second": "#3a2d50",
            "panel": "#312744",
            "panel_alt": "#3f3158",
            "text": "#fbf7ff",
            "muted": "#d5c7e7",
            "accent": "#d6b8f3",
            "accent_soft": "#51406e",
            "accent_strong": "#ecdfff",
            "border": "#7d6899",
            "success": "#87d7a0",
            "sidebar": "rgba(42, 33, 58, 0.96)",
            "button_text": "#ffffff",
        },
    }
    palette = themes[theme_name]
    st.markdown(
        f"""
        <style>
            :root {{
                --bg: {palette["bg"]};
                --bg-second: {palette["bg_second"]};
                --panel: {palette["panel"]};
                --panel-alt: {palette["panel_alt"]};
                --text: {palette["text"]};
                --muted: {palette["muted"]};
                --accent: {palette["accent"]};
                --accent-soft: {palette["accent_soft"]};
                --accent-strong: {palette["accent_strong"]};
                --border: {palette["border"]};
                --success: {palette["success"]};
                --button-text: {palette["button_text"]};
            }}
            .stApp {{
                background:
                    radial-gradient(circle at 0% 0%, rgba(214, 184, 243, 0.22) 0%, transparent 28%),
                    radial-gradient(circle at 100% 12%, rgba(244, 233, 255, 0.55) 0%, transparent 20%),
                    linear-gradient(180deg, var(--bg) 0%, var(--bg-second) 100%);
                color: var(--text);
            }}
            .main .block-container {{
                padding-top: 1.35rem;
                padding-bottom: 3rem;
            }}
            h1, h2, h3, h4, h5, h6, p, label, span {{
                color: var(--text);
            }}
            [data-testid="stSidebar"] {{
                background: {palette["sidebar"]};
                border-right: 1px solid var(--border);
            }}
            [data-testid="stMetric"] {{
                background: linear-gradient(180deg, rgba(255,255,255,0.2), rgba(255,255,255,0.05));
                border: 1px solid var(--border);
                border-radius: 20px;
                padding: 0.7rem;
            }}
            [data-testid="stMetricValue"],
            [data-testid="stMetricLabel"] {{
                color: var(--text);
            }}
            div[role="radiogroup"] {{
                gap: 0.5rem;
                flex-wrap: wrap;
            }}
            div[role="radiogroup"] label {{
                background: rgba(255,255,255,0.42);
                border: 1px solid var(--border);
                border-radius: 999px;
                padding: 0.45rem 0.95rem;
            }}
            .hero {{
                background:
                    linear-gradient(135deg, rgba(244,233,255,0.9) 0%, rgba(255,255,255,0.68) 100%),
                    var(--panel);
                border: 1px solid var(--border);
                border-radius: 30px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                box-shadow: 0 18px 50px rgba(86, 66, 117, 0.08);
            }}
            .hero h1 {{
                margin-bottom: 0.45rem;
                font-size: 3rem;
                letter-spacing: -0.03em;
            }}
            .small-note {{
                color: var(--muted);
                font-size: 1rem;
            }}
            .section-intro {{
                color: var(--muted);
                margin-bottom: 0.8rem;
            }}
            .quick-card {{
                background: var(--panel-alt);
                border: 1px solid var(--border);
                border-radius: 20px;
                padding: 1rem;
                margin-bottom: 1rem;
            }}
            .action-card {{
                background: linear-gradient(180deg, rgba(255,255,255,0.26), rgba(255,255,255,0.08));
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 1rem;
                min-height: 138px;
                margin-bottom: 0.6rem;
            }}
            .action-title {{
                color: var(--text);
                font-size: 1rem;
                font-weight: 700;
                margin-bottom: 0.35rem;
            }}
            .inline-kicker {{
                color: var(--muted);
                font-size: 0.95rem;
            }}
            .stat-strip {{
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.9rem;
                margin: 1rem 0 1.1rem;
            }}
            .stat-card {{
                background: var(--panel-alt);
                border: 1px solid var(--border);
                border-radius: 22px;
                padding: 1rem;
            }}
            .stat-label {{
                color: var(--muted);
                font-size: 0.92rem;
                margin-bottom: 0.25rem;
            }}
            .stat-value {{
                color: var(--text);
                font-size: 1.7rem;
                font-weight: 700;
            }}
            .tag {{
                display: inline-block;
                background: var(--accent-soft);
                color: var(--text);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 999px;
                padding: 0.2rem 0.7rem;
                margin-right: 0.35rem;
                margin-bottom: 0.35rem;
                font-size: 0.84rem;
            }}
            .soft-divider {{
                height: 1px;
                width: 100%;
                background: linear-gradient(90deg, transparent, var(--border), transparent);
                margin: 0.7rem 0 1rem;
            }}
            .stButton > button {{
                border-radius: 999px;
                border: 1px solid var(--accent);
                background: linear-gradient(180deg, var(--accent), var(--accent-strong));
                color: var(--button-text);
                width: 100%;
            }}
            .stDownloadButton > button {{
                border-radius: 999px;
            }}
            div[data-baseweb="select"] > div,
            div[data-baseweb="input"] > div,
            textarea,
            input {{
                background: rgba(255,255,255,0.06);
                color: var(--text);
            }}
            [data-testid="stExpander"] {{
                border: 1px solid var(--border);
                border-radius: 18px;
                background: rgba(255,255,255,0.04);
            }}
            @media (max-width: 900px) {{
                .main .block-container {{
                    padding-top: 1rem;
                    padding-left: 0.8rem;
                    padding-right: 0.8rem;
                    padding-bottom: 2rem;
                }}
                .hero {{
                    padding: 1.15rem;
                    border-radius: 24px;
                }}
                .hero h1 {{
                    font-size: 2rem;
                    line-height: 1.08;
                }}
                .stat-strip {{
                    grid-template-columns: 1fr;
                }}
                [data-testid="column"] {{
                    width: 100% !important;
                    flex: 1 1 100% !important;
                    min-width: 100% !important;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_state() -> None:
    if "theme" not in st.session_state:
        st.session_state.theme = "Claro"
    if "new_form_version" not in st.session_state:
        st.session_state.new_form_version = 0
    if "active_section" not in st.session_state:
        st.session_state.active_section = "Inicio"


def reset_new_recipe_form() -> None:
    st.session_state.new_form_version += 1


def get_recipe_defaults(recipe: dict | None = None) -> dict:
    if recipe is None:
        return {
            "name": "",
            "description": "",
            "category": "",
            "prep_time_minutes": 30,
            "servings": 2,
            "difficulty": "Facil",
            "notes": "",
            "favorite": False,
            "ingredients": [{"quantity": "", "ingredient_name": ""}],
            "steps": [""],
        }

    return {
        "name": recipe["name"],
        "description": recipe["description"],
        "category": recipe["category"],
        "prep_time_minutes": recipe["prep_time_minutes"],
        "servings": recipe["servings"],
        "difficulty": recipe["difficulty"],
        "notes": recipe["notes"],
        "favorite": bool(recipe["favorite"]),
        "ingredients": [
            {
                "quantity": ingredient["quantity"],
                "ingredient_name": ingredient["ingredient_name"],
            }
            for ingredient in recipe["ingredients"]
        ]
        or [{"quantity": "", "ingredient_name": ""}],
        "steps": [step["instruction"] for step in recipe["steps"]] or [""],
    }


def payload_from_editor(widget_prefix: str, ingredient_rows: list[dict], step_rows: list[str]) -> RecipePayload:
    return RecipePayload(
        name=st.session_state.get(f"{widget_prefix}_recipe_name", ""),
        description=st.session_state.get(f"{widget_prefix}_recipe_description", ""),
        category=st.session_state.get(f"{widget_prefix}_recipe_category", ""),
        prep_time_minutes=int(st.session_state.get(f"{widget_prefix}_recipe_time", 0) or 0),
        servings=int(st.session_state.get(f"{widget_prefix}_recipe_servings", 0) or 0),
        difficulty=st.session_state.get(f"{widget_prefix}_recipe_difficulty", "Media"),
        notes=st.session_state.get(f"{widget_prefix}_recipe_notes", ""),
        favorite=bool(st.session_state.get(f"{widget_prefix}_recipe_favorite", False)),
        ingredients=clean_ingredients(ingredient_rows),
        steps=clean_steps(step_rows),
    )


def render_editor(widget_prefix: str, defaults: dict) -> tuple[list[dict], list[str], list]:
    st.text_input(
        "Nombre de la receta",
        key=f"{widget_prefix}_recipe_name",
        value=defaults["name"],
        placeholder="Ejemplo: Sopa de pollo",
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input(
            "Categoria",
            key=f"{widget_prefix}_recipe_category",
            value=defaults["category"],
            placeholder="Almuerzo, postre, cena...",
        )
    with col2:
        st.number_input(
            "Tiempo (minutos)",
            min_value=0,
            step=5,
            key=f"{widget_prefix}_recipe_time",
            value=defaults["prep_time_minutes"],
        )
    with col3:
        st.number_input(
            "Porciones",
            min_value=0,
            step=1,
            key=f"{widget_prefix}_recipe_servings",
            value=defaults["servings"],
        )

    col4, col5 = st.columns([2, 1])
    with col4:
        difficulty_options = ["Facil", "Media", "Dificil"]
        st.selectbox(
            "Dificultad",
            difficulty_options,
            key=f"{widget_prefix}_recipe_difficulty",
            index=difficulty_options.index(defaults["difficulty"]),
        )
    with col5:
        st.checkbox(
            "Marcar como favorita",
            key=f"{widget_prefix}_recipe_favorite",
            value=defaults["favorite"],
        )

    st.text_area(
        "Descripcion",
        key=f"{widget_prefix}_recipe_description",
        value=defaults["description"],
        placeholder="Cuenta brevemente que hace especial esta receta.",
        height=100,
    )

    st.subheader("Ingredientes")
    ingredients_df = pd.DataFrame(defaults["ingredients"])
    edited_ingredients = st.data_editor(
        ingredients_df,
        key=f"{widget_prefix}_ingredients_editor",
        num_rows="dynamic",
        width="stretch",
        column_config={
            "quantity": "Cantidad",
            "ingredient_name": "Ingrediente",
        },
    )

    st.subheader("Pasos")
    steps_buffer_key = f"{widget_prefix}_steps_buffer"
    if steps_buffer_key not in st.session_state:
        st.session_state[steps_buffer_key] = defaults["steps"]

    step_rows: list[str] = []
    current_steps = st.session_state[steps_buffer_key] or [""]
    for index, current_step in enumerate(current_steps, start=1):
        step_key = f"{widget_prefix}_step_{index}"
        step_rows.append(
            st.text_area(
                f"Paso {index}",
                key=step_key,
                value=current_step,
                placeholder="Describe este paso...",
                height=95,
            )
        )
    st.session_state[steps_buffer_key] = step_rows or [""]

    add_col, remove_col = st.columns(2)
    with add_col:
        if st.button("Agregar otro paso", key=f"{widget_prefix}_add_step"):
            st.session_state[steps_buffer_key] = (step_rows or [""]) + [""]
            st.rerun()
    with remove_col:
        if len(current_steps) > 1 and st.button("Quitar ultimo paso", key=f"{widget_prefix}_remove_step"):
            st.session_state[steps_buffer_key] = step_rows[:-1] or [""]
            st.rerun()

    st.text_area(
        "Notas personales",
        key=f"{widget_prefix}_recipe_notes",
        value=defaults["notes"],
        placeholder="Trucos, observaciones o ideas para mejorar la receta.",
        height=100,
    )
    uploaded_files = st.file_uploader(
        "Fotos de referencia",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        key=f"{widget_prefix}_recipe_images",
    )

    return edited_ingredients.to_dict("records"), step_rows, uploaded_files


def render_recipe_card(recipe: dict, *, show_full: bool = False) -> None:
    tags = [
        recipe["category"] or "Sin categoria",
        f'{recipe["prep_time_minutes"]} min' if recipe["prep_time_minutes"] else "Tiempo libre",
        f'{recipe["servings"]} porciones' if recipe["servings"] else "Porciones libres",
        recipe["difficulty"],
    ]
    with st.container(border=True):
        title_col, favorite_col = st.columns([5, 2])
        with title_col:
            st.markdown(f"### {recipe['name']}")
        with favorite_col:
            if recipe["favorite"]:
                st.markdown("`Favorita`")

        st.markdown("".join([f'<span class="tag">{tag}</span>' for tag in tags]), unsafe_allow_html=True)
        st.caption(recipe["description"] or "Sin descripcion todavia.")

        if recipe["images"]:
            image_cols = st.columns(min(len(recipe["images"]), 3))
            for index, image in enumerate(recipe["images"][:3]):
                image_path = Path(image["file_path"])
                if image_path.exists():
                    image_cols[index].image(str(image_path), width="stretch")

        if show_full:
            st.markdown("**Ingredientes**")
            for ingredient in recipe["ingredients"]:
                amount = f'{ingredient["quantity"]} - ' if ingredient["quantity"] else ""
                st.write(f"- {amount}{ingredient['ingredient_name']}")

            st.markdown("**Pasos**")
            for step in recipe["steps"]:
                st.write(f"{step['step_number']}. {step['instruction']}")

            if recipe["notes"]:
                st.markdown("**Notas**")
                st.write(recipe["notes"])
        else:
            with st.expander("Ver receta completa"):
                render_recipe_card(recipe, show_full=True)


def render_recipe_collection(title: str, recipes: list[dict], empty_message: str) -> None:
    st.subheader(title)
    if not recipes:
        st.info(empty_message)
        return
    for recipe in recipes:
        render_recipe_card(recipe, show_full=False)


def build_full_recipe_list() -> list[dict]:
    recipes = []
    for summary in list_recipes():
        full_recipe = get_recipe(summary["id"])
        if full_recipe:
            recipes.append(full_recipe)
    return recipes


ensure_state()
seed_sample_data()
apply_theme(st.session_state.theme)

stats = get_dashboard_stats()
full_recipes = build_full_recipe_list()
favorite_recipes = [recipe for recipe in full_recipes if recipe["favorite"]]
recent_recipes = sorted(full_recipes, key=lambda recipe: recipe["updated_at"], reverse=True)

st.sidebar.title("Recetario Inteligente")
selected_theme = st.sidebar.radio(
    "Apariencia",
    ["Claro", "Oscuro"],
    index=0 if st.session_state.theme == "Claro" else 1,
)
if selected_theme != st.session_state.theme:
    st.session_state.theme = selected_theme
    st.rerun()

st.sidebar.metric("Recetas guardadas", stats["recipes"])
st.sidebar.metric("Ingredientes unicos", stats["ingredients"])
st.sidebar.metric("Favoritas", stats["favorites"])
st.sidebar.caption("Las favoritas aparecen en Inicio y tambien pueden filtrarse en Buscar.")

st.markdown(
    """
    <div class="hero">
        <h1>Recetario Inteligente</h1>
        <p class="small-note">
            Guarda recetas, adjunta fotos, encuentra ideas segun tus ingredientes y revisa tus favoritas sin perderte entre formularios.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="stat-strip">
        <div class="stat-card">
            <div class="stat-label">Recetas guardadas</div>
            <div class="stat-value">{stats["recipes"]}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Favoritas visibles</div>
            <div class="stat-value">{stats["favorites"]}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Ingredientes registrados</div>
            <div class="stat-value">{stats["ingredients"]}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

sections = ["Inicio", "Agregar receta", "Buscar recetas", "Mi cocina", "Administrar", "Compartir"]
active_section = st.radio(
    "Navegacion",
    sections,
    key="active_section",
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)

if active_section == "Inicio":
    st.markdown(
        '<p class="section-intro">Aqui tienes una vista rapida de lo mas importante de tu recetario.</p>',
        unsafe_allow_html=True,
    )
    quick_choice = st.selectbox(
        "Que quieres hacer hoy?",
        [
            "Ver favoritas",
            "Buscar una receta",
            "Agregar una receta nueva",
            "Ver que puedo cocinar con mis ingredientes",
        ],
    )
    quick_messages = {
        "Ver favoritas": "Tus favoritas aparecen justo abajo y tambien puedes filtrarlas en la pestana Buscar recetas.",
        "Buscar una receta": "Usa la pestana Buscar recetas para filtrar por nombre, ingrediente, categoria o solo favoritas.",
        "Agregar una receta nueva": "Ve a Agregar receta para guardar una nueva con fotos, pasos y notas.",
        "Ver que puedo cocinar con mis ingredientes": "La pestana Mi cocina compara tus ingredientes con todas las recetas guardadas.",
    }
    st.markdown(
        f"""
        <div class="quick-card">
            <strong>Sugerencia rapida</strong>
            <p class="inline-kicker">{quick_messages[quick_choice]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    action_col1, action_col2, action_col3 = st.columns(3)
    with action_col1:
        st.markdown(
            """
            <div class="action-card">
                <div class="action-title">Guardar una receta</div>
                <p class="inline-kicker">Entra directo al formulario para anadir ingredientes, pasos y fotos.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Ir a Agregar receta", key="go_add"):
            st.session_state.active_section = "Agregar receta"
            st.rerun()
    with action_col2:
        st.markdown(
            """
            <div class="action-card">
                <div class="action-title">Buscar o filtrar</div>
                <p class="inline-kicker">Encuentra recetas por nombre, ingredientes, categoria o solo favoritas.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Ir a Buscar recetas", key="go_search"):
            st.session_state.active_section = "Buscar recetas"
            st.rerun()
    with action_col3:
        st.markdown(
            """
            <div class="action-card">
                <div class="action-title">Usar lo que tienes</div>
                <p class="inline-kicker">Compara tu cocina actual con las recetas guardadas y mira coincidencias.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Ir a Mi cocina", key="go_pantry"):
            st.session_state.active_section = "Mi cocina"
            st.rerun()
    col_favorites, col_recent = st.columns(2)
    with col_favorites:
        render_recipe_collection(
            "Favoritas",
            favorite_recipes[:3],
            "Todavia no has marcado recetas como favoritas.",
        )
    with col_recent:
        render_recipe_collection(
            "Recetas guardadas recientemente",
            recent_recipes[:4],
            "Todavia no hay recetas guardadas.",
        )

if active_section == "Agregar receta":
    st.subheader("Nueva receta")
    st.caption("Agrega la receta con ingredientes, pasos, notas y fotos.")
    new_widget_prefix = f"new_{st.session_state.new_form_version}"
    ingredient_rows, step_rows, uploaded_files = render_editor(
        new_widget_prefix,
        get_recipe_defaults(),
    )

    col_save, col_reset = st.columns([1, 1])
    with col_save:
        if st.button("Guardar receta", key="save_new_recipe"):
            try:
                payload = payload_from_editor(new_widget_prefix, ingredient_rows, step_rows)
                create_recipe(payload, uploaded_files)
                reset_new_recipe_form()
                st.toast("Receta guardada con exito.")
                st.success("La receta se guardo correctamente.")
                st.balloons()
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
    with col_reset:
        if st.button("Limpiar formulario", key="clear_new_recipe"):
            reset_new_recipe_form()
            st.rerun()

if active_section == "Buscar recetas":
    st.subheader("Buscar recetas")
    st.caption("Puedes explorar todas tus recetas o filtrar por nombre, categoria e ingredientes.")
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
    with filter_col1:
        search_term = st.text_input(
            "Busca por nombre o ingrediente",
            placeholder="Ejemplo: pollo, pasta, tomate...",
        )
    with filter_col2:
        categories = ["Todas"] + get_categories()
        selected_category = st.selectbox("Categoria", categories)
    with filter_col3:
        favorites_only = st.checkbox("Solo favoritas", value=False)

    results = list_recipes(search_term, selected_category)
    if favorites_only:
        results = [recipe for recipe in results if recipe["favorite"]]

    if not results:
        st.info("No encontramos recetas con esos filtros.")
    else:
        st.caption(f"{len(results)} receta(s) encontradas")
        for recipe_summary in results:
            full_recipe = get_recipe(recipe_summary["id"])
            if full_recipe:
                render_recipe_card(full_recipe, show_full=False)

if active_section == "Mi cocina":
    st.subheader("Ingredientes que tienes ahora")
    st.caption("Te sugerimos recetas completas o casi completas con base en tu cocina actual.")
    known_ingredients = get_all_known_ingredients()
    selected_known_ingredients = st.multiselect(
        "Selecciona ingredientes guardados",
        known_ingredients,
        placeholder="Elige de la lista si ya existen en tus recetas",
    )
    extra_ingredients = st.text_area(
        "Agrega otros ingredientes separados por coma o por linea",
        placeholder="Ejemplo: pollo, arroz, cebolla, crema",
        height=100,
    )
    pantry_items = [
        item.strip()
        for item in selected_known_ingredients + extra_ingredients.replace("\n", ",").split(",")
        if item.strip()
    ]

    if pantry_items:
        st.markdown("**Ingredientes detectados**")
        st.write(", ".join(pantry_items))

    suggestions = get_pantry_suggestions(pantry_items) if pantry_items else []
    if not pantry_items:
        st.info("Escribe o selecciona ingredientes para ver sugerencias.")
    elif not suggestions:
        st.warning("No hay coincidencias aun. Intenta con mas ingredientes o agrega mas recetas.")
    else:
        exact_matches = [item for item in suggestions if item["can_make_now"]]
        if exact_matches:
            st.success(f"Puedes preparar {len(exact_matches)} receta(s) completas con lo que tienes.")
        else:
            st.warning("No hay recetas completas con esos ingredientes, pero si hay opciones cercanas.")

        for suggestion in suggestions:
            recipe = suggestion["recipe"]
            missing_text = ", ".join(suggestion["missing_ingredients"]) if suggestion["missing_ingredients"] else "No te falta nada"
            with st.container(border=True):
                top_left, top_right = st.columns([5, 2])
                with top_left:
                    st.markdown(f"### {recipe['name']}")
                with top_right:
                    st.markdown(f"`{suggestion['match_percentage']}% coincidencia`")
                st.caption(
                    f"Ingredientes cubiertos: {suggestion['matched_ingredients']}/{suggestion['total_ingredients']}"
                )
            if suggestion["can_make_now"]:
                st.success("Lista para cocinar ahora")
            else:
                st.info(f"Te falta: {missing_text}")
            with st.expander("Ver detalles de la receta"):
                render_recipe_card(recipe, show_full=True)

if active_section == "Administrar":
    st.subheader("Editar o eliminar recetas")
    st.caption("Selecciona una receta guardada para cambiar datos, marcar favorita o borrar contenido.")
    all_recipes = list_recipes()
    recipe_options = {recipe["name"]: recipe["id"] for recipe in all_recipes}
    selected_recipe_name = st.selectbox("Selecciona una receta", [""] + list(recipe_options.keys()))
    if selected_recipe_name:
        selected_recipe = get_recipe(recipe_options[selected_recipe_name])
        if selected_recipe:
            st.markdown("**Vista previa actual**")
            render_recipe_card(selected_recipe, show_full=False)

            existing_images = selected_recipe["images"]
            if existing_images:
                st.markdown("**Imagenes actuales**")
                image_cols = st.columns(min(len(existing_images), 3))
                for index, image in enumerate(existing_images[:3]):
                    image_path = Path(image["file_path"])
                    if image_path.exists():
                        image_cols[index].image(
                            str(image_path),
                            caption=image["original_name"],
                            width="stretch",
                        )

            replace_images = st.checkbox("Reemplazar imagenes actuales", value=False)
            edit_widget_prefix = f"edit_{selected_recipe['id']}"
            edit_ingredients, edit_steps, new_images = render_editor(
                edit_widget_prefix,
                get_recipe_defaults(selected_recipe),
            )

            col_update, col_delete = st.columns([1, 1])
            with col_update:
                if st.button("Guardar cambios", key="update_recipe_button"):
                    try:
                        payload = payload_from_editor(edit_widget_prefix, edit_ingredients, edit_steps)
                        update_recipe(selected_recipe["id"], payload, new_images, replace_images=replace_images)
                        st.toast("Receta actualizada.")
                        st.success("La receta se actualizo correctamente.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
            with col_delete:
                if st.button("Eliminar receta", key="delete_recipe_button"):
                    delete_recipe(selected_recipe["id"])
                    st.toast("Receta eliminada.")
                    st.success("La receta fue eliminada.")
                    st.rerun()

if active_section == "Compartir":
    st.subheader("Compartir la app")
    st.caption("Esta pestana aparece porque agregue una guia para volver publica la app y verla desde otro movil fuera de tu Wi-Fi.")
    st.info("Si solo la usaras en tu PC o en tu misma red, puedes ignorar esta pestana por completo.")

    with st.expander("Que es la ventana que aparece arriba?"):
        st.write(
            "Es el menu de Streamlit. Desde ahi puedes recargar la app, cambiar el tema del visor y abrir la opcion de publicacion. No es un error."
        )

    with st.expander("Como verla desde otro movil que no este en mi Wi-Fi?"):
        st.write("1. Sube esta carpeta a GitHub.")
        st.write("2. Entra a Streamlit Community Cloud.")
        st.write("3. Crea una app usando este proyecto y selecciona `app.py`.")
        st.write("4. Publica y usa el enlace publico generado.")

    with st.expander("Hay una forma temporal para compartir rapido?"):
        st.write("Si, con un tunel como `ngrok` o `cloudflared`, pero requiere instalar otra herramienta.")
        st.write("La forma mas estable para este proyecto sigue siendo Streamlit Community Cloud.")
