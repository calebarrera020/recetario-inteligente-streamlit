from __future__ import annotations

import base64
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
    update_recipe,
)

st.set_page_config(
    page_title="Recetario Inteligente",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def apply_theme(theme_name: str) -> None:
    themes = {
        "Claro": {
            "bg": "#fff9fc",
            "bg_second": "#f6ebfb",
            "panel": "#fffdfd",
            "panel_alt": "#fcf5ff",
            "text": "#3d3150",
            "muted": "#8f819f",
            "accent": "#d8b9f1",
            "accent_soft": "#f3e6ff",
            "accent_strong": "#b486de",
            "border": "#eadbf8",
            "shadow": "rgba(137, 102, 178, 0.12)",
            "button_text": "#ffffff",
            "shell_shadow": "rgba(126, 93, 168, 0.22)",
            "field_bg": "#fffdfd",
            "field_text": "#3d3150",
            "field_placeholder": "#8f819f",
        },
        "Oscuro": {
            "bg": "#2e2441",
            "bg_second": "#3f3158",
            "panel": "#372b4c",
            "panel_alt": "#43325c",
            "text": "#fbf7ff",
            "muted": "#d7cbe6",
            "accent": "#d9bdf2",
            "accent_soft": "#564170",
            "accent_strong": "#efdefe",
            "border": "#826c9b",
            "shadow": "rgba(0, 0, 0, 0.18)",
            "button_text": "#2b2140",
            "shell_shadow": "rgba(0, 0, 0, 0.28)",
            "field_bg": "#f5eefc",
            "field_text": "#2f2144",
            "field_placeholder": "#7d6b92",
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
                --shadow: {palette["shadow"]};
                --button-text: {palette["button_text"]};
                --shell-shadow: {palette["shell_shadow"]};
                --field-bg: {palette["field_bg"]};
                --field-text: {palette["field_text"]};
                --field-placeholder: {palette["field_placeholder"]};
            }}
            .stApp {{
                background:
                    radial-gradient(circle at 0% 0%, rgba(216,185,241,0.22) 0%, transparent 28%),
                    radial-gradient(circle at 100% 12%, rgba(243,230,255,0.52) 0%, transparent 20%),
                    linear-gradient(180deg, var(--bg) 0%, var(--bg-second) 100%);
                color: var(--text);
            }}
            .main .block-container {{
                max-width: 460px;
                padding-top: 0.65rem;
                padding-bottom: 1.1rem;
                padding-left: 0.55rem;
                padding-right: 0.55rem;
            }}
            [data-testid="stSidebar"],
            [data-testid="collapsedControl"] {{
                display: none;
            }}
            h1, h2, h3, h4, h5, h6, p, span, label {{
                color: var(--text);
            }}
            div[role="radiogroup"] {{
                gap: 0.4rem;
                flex-wrap: wrap;
            }}
            div[role="radiogroup"] label {{
                background: rgba(255,255,255,0.4);
                border: 1px solid var(--border);
                border-radius: 999px;
                padding: 0.42rem 0.82rem;
            }}
            .phone-shell {{
                background: linear-gradient(180deg, rgba(255,255,255,0.45), rgba(255,255,255,0.12));
                border: 1px solid var(--border);
                border-radius: 34px;
                box-shadow: 0 28px 70px var(--shell-shadow);
                padding: 0.75rem;
            }}
            .app-top {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 1rem;
            }}
            .hello-title {{
                font-size: 1.62rem;
                font-weight: 800;
                line-height: 1.06;
                margin: 0;
            }}
            .hello-subtitle {{
                color: var(--muted);
                margin-top: 0.2rem;
                font-size: 0.88rem;
            }}
            .search-block {{
                background: rgba(255,255,255,0.58);
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 0.24rem 0.65rem 0.05rem;
                margin-bottom: 0.75rem;
            }}
            .category-chip {{
                text-align: center;
                padding: 0.2rem;
            }}
            .category-circle {{
                width: 48px;
                height: 48px;
                border-radius: 999px;
                background: linear-gradient(180deg, rgba(255,255,255,0.85), rgba(255,255,255,0.4));
                border: 1px solid var(--border);
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 0.35rem;
                font-size: 1.2rem;
                box-shadow: 0 10px 22px var(--shadow);
            }}
            .category-text {{
                color: var(--muted);
                font-size: 0.68rem;
            }}
            .section-title {{
                font-size: 0.98rem;
                font-weight: 800;
                margin: 0.75rem 0 0.55rem;
            }}
            .recipe-card {{
                background: var(--panel);
                border: 1px solid var(--border);
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 12px 28px var(--shadow);
                margin-bottom: 0.85rem;
            }}
            .recipe-thumb {{
                height: 112px;
                background: linear-gradient(135deg, var(--accent-soft), rgba(255,255,255,0.7));
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2rem;
            }}
            .recipe-body {{
                padding: 0.72rem 0.78rem 0.82rem;
            }}
            .recipe-title {{
                margin: 0;
                font-weight: 800;
                font-size: 0.94rem;
                line-height: 1.2;
            }}
            .recipe-soft {{
                color: var(--muted);
                font-size: 0.78rem;
                margin-top: 0.28rem;
                margin-bottom: 0.45rem;
            }}
            .mini-chip {{
                display: inline-block;
                background: var(--accent-soft);
                color: var(--text);
                border-radius: 999px;
                padding: 0.18rem 0.55rem;
                font-size: 0.76rem;
                margin-right: 0.28rem;
                margin-bottom: 0.28rem;
            }}
            .detail-hero {{
                background: var(--panel);
                border: 1px solid var(--border);
                border-radius: 24px;
                padding: 0.75rem;
                box-shadow: 0 14px 32px var(--shadow);
                margin-bottom: 1rem;
            }}
            .detail-title {{
                font-size: 1.15rem;
                font-weight: 800;
                line-height: 1.14;
                margin: 0.65rem 0 0.28rem;
            }}
            .stats-row {{
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 0.45rem;
                margin-top: 0.7rem;
            }}
            .stat-pill {{
                background: rgba(255,255,255,0.45);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 0.55rem 0.4rem;
                text-align: center;
            }}
            .stat-pill strong {{
                display: block;
                font-size: 0.78rem;
            }}
            .stat-pill span {{
                color: var(--muted);
                font-size: 0.72rem;
            }}
            .ingredient-card, .step-card {{
                background: rgba(255,255,255,0.46);
                border: 1px solid var(--border);
                border-radius: 17px;
                padding: 0.8rem;
                margin-bottom: 0.55rem;
            }}
            .step-number {{
                width: 30px;
                height: 30px;
                border-radius: 999px;
                background: var(--accent-strong);
                color: var(--button-text);
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                margin-right: 0.5rem;
            }}
            .soft-divider {{
                height: 1px;
                width: 100%;
                background: linear-gradient(90deg, transparent, var(--border), transparent);
                margin: 0.75rem 0;
            }}
            .stButton > button {{
                border-radius: 999px;
                border: 1px solid var(--accent);
                background: linear-gradient(180deg, var(--accent), var(--accent-strong));
                color: var(--button-text);
                width: 100%;
                min-height: 44px;
                font-weight: 700;
                box-shadow: 0 8px 18px var(--shadow);
            }}
            .stFormSubmitButton > button {{
                border-radius: 999px;
                border: 1px solid var(--accent);
                background: linear-gradient(180deg, var(--accent), var(--accent-strong));
                color: var(--button-text);
                width: 100%;
                min-height: 44px;
                font-weight: 700;
                box-shadow: 0 8px 18px var(--shadow);
            }}
            .stTextInput > div > div,
            .stTextArea > div > div,
            .stNumberInput > div > div,
            .stSelectbox > div > div,
            div[data-baseweb="select"] > div,
            div[data-baseweb="input"] > div,
            div[data-baseweb="textarea"] > div,
            [data-baseweb="base-input"] {{
                background: var(--field-bg) !important;
                color: var(--field-text) !important;
                border: 1px solid var(--border) !important;
                border-radius: 16px !important;
                box-shadow: none !important;
                opacity: 1 !important;
            }}
            .stTextInput input,
            .stTextArea textarea,
            .stNumberInput input,
            .stSelectbox input,
            .stApp input:not([type="checkbox"]):not([type="radio"]),
            .stApp textarea,
            [data-baseweb="base-input"] input,
            [data-baseweb="textarea"] textarea,
            [contenteditable="true"] {{
                color: var(--field-text) !important;
                -webkit-text-fill-color: var(--field-text) !important;
                caret-color: var(--field-text) !important;
                background: transparent !important;
                opacity: 1 !important;
                text-shadow: none !important;
            }}
            [data-testid="stTextArea"] textarea,
            [data-testid="stTextInput"] input,
            [data-testid="stNumberInput"] input,
            [data-baseweb="base-input"] input,
            [data-baseweb="textarea"] textarea {{
                color: var(--field-text) !important;
                -webkit-text-fill-color: var(--field-text) !important;
                caret-color: var(--field-text) !important;
                background: transparent !important;
            }}
            .stTextInput input:focus,
            .stTextArea textarea:focus,
            .stNumberInput input:focus,
            .stApp input:focus,
            .stApp textarea:focus {{
                color: var(--field-text) !important;
                -webkit-text-fill-color: var(--field-text) !important;
                background: transparent !important;
                outline: none !important;
            }}
            [data-testid="stTextArea"] textarea::placeholder,
            [data-testid="stTextInput"] input::placeholder,
            [data-testid="stNumberInput"] input::placeholder,
            .stApp input::placeholder,
            .stApp textarea::placeholder,
            [data-baseweb="textarea"] textarea::placeholder {{
                color: var(--field-placeholder) !important;
                -webkit-text-fill-color: var(--field-placeholder) !important;
                opacity: 1 !important;
            }}
            [data-testid="stTextArea"] label,
            [data-testid="stTextInput"] label,
            [data-testid="stNumberInput"] label,
            [data-testid="stSelectbox"] label,
            [data-testid="stCheckbox"] label {{
                color: var(--text) !important;
            }}
            [data-testid="stDataFrame"] {{
                border-radius: 18px !important;
                overflow: hidden !important;
                border: 1px solid var(--border) !important;
                background: var(--field-bg) !important;
            }}
            [data-testid="stDataFrame"] [role="grid"],
            [data-testid="stDataFrame"] [role="rowgroup"],
            [data-testid="stDataFrame"] [role="row"],
            [data-testid="stDataFrame"] [role="gridcell"],
            [data-testid="stDataFrame"] [role="columnheader"] {{
                background: var(--field-bg) !important;
                color: var(--field-text) !important;
                border-color: var(--border) !important;
            }}
            [data-testid="stDataFrame"] input,
            [data-testid="stDataFrame"] textarea,
            [data-testid="stDataFrame"] [contenteditable="true"] {{
                color: var(--field-text) !important;
                -webkit-text-fill-color: var(--field-text) !important;
                caret-color: var(--field-text) !important;
                background: transparent !important;
            }}
            [data-testid="stDataFrame"] svg,
            [data-testid="stDataFrame"] svg path,
            [data-testid="stElementToolbar"] svg,
            [data-testid="stElementToolbar"] svg path,
            [data-testid="stDataFrameToolbar"] svg,
            [data-testid="stDataFrameToolbar"] svg path,
            [data-testid="stDataFrameToolbar"] button,
            [data-testid="stDataFrameToolbar"] span {{
                color: var(--field-text) !important;
                fill: var(--field-text) !important;
                stroke: var(--field-text) !important;
                opacity: 1 !important;
            }}
            [data-testid="stExpander"] {{
                border: 1px solid var(--border);
                border-radius: 18px;
                background: rgba(255,255,255,0.06);
            }}
            @media (max-width: 520px) {{
                .main .block-container {{
                    padding-left: 0.42rem;
                    padding-right: 0.42rem;
                }}
                .phone-shell {{
                    border-radius: 24px;
                    padding: 0.58rem;
                }}
                div[role="radiogroup"] label {{
                    padding: 0.34rem 0.66rem;
                }}
                .recipe-card {{
                    border-radius: 18px;
                }}
                .detail-hero {{
                    border-radius: 20px;
                    padding: 0.62rem;
                }}
                .ingredient-card, .step-card {{
                    padding: 0.68rem;
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
    if "current_section" not in st.session_state:
        st.session_state.current_section = "Recetas"
    if "nav_choice" not in st.session_state:
        st.session_state.nav_choice = "Recetas"
    if "pending_section" not in st.session_state:
        st.session_state.pending_section = None
    if "selected_recipe_id" not in st.session_state:
        st.session_state.selected_recipe_id = None
    if "detail_view" not in st.session_state:
        st.session_state.detail_view = "Ingredientes"
    if "home_search" not in st.session_state:
        st.session_state.home_search = ""
    if "flash_message" not in st.session_state:
        st.session_state.flash_message = ""
    if "flash_kind" not in st.session_state:
        st.session_state.flash_kind = "success"


def set_flash_message(message: str, kind: str = "success") -> None:
    st.session_state.flash_message = message
    st.session_state.flash_kind = kind


def show_flash_message() -> None:
    message = st.session_state.get("flash_message", "")
    if not message:
        return
    kind = st.session_state.get("flash_kind", "success")
    if kind == "error":
        st.error(message)
    elif kind == "warning":
        st.warning(message)
    else:
        st.success(message)
    st.session_state.flash_message = ""


def greeting_text() -> str:
    return "Bienvenida"


def reset_new_recipe_form() -> None:
    st.session_state.new_form_version += 1


def open_recipe_detail(recipe_id: int) -> None:
    st.session_state.selected_recipe_id = recipe_id
    st.session_state.pending_section = "Detalle"


def close_recipe_detail() -> None:
    st.session_state.selected_recipe_id = None
    st.session_state.pending_section = "Recetas"


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
            {"quantity": ingredient["quantity"], "ingredient_name": ingredient["ingredient_name"]}
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
    st.text_input("Nombre de la receta", key=f"{widget_prefix}_recipe_name", value=defaults["name"])
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Categoria", key=f"{widget_prefix}_recipe_category", value=defaults["category"])
    with col2:
        st.selectbox(
            "Dificultad",
            ["Facil", "Media", "Dificil"],
            key=f"{widget_prefix}_recipe_difficulty",
            index=["Facil", "Media", "Dificil"].index(defaults["difficulty"]),
        )
    col3, col4 = st.columns(2)
    with col3:
        st.number_input("Tiempo (minutos)", min_value=0, step=5, key=f"{widget_prefix}_recipe_time", value=defaults["prep_time_minutes"])
    with col4:
        st.number_input("Porciones", min_value=0, step=1, key=f"{widget_prefix}_recipe_servings", value=defaults["servings"])
    st.checkbox("Marcar como favorita", key=f"{widget_prefix}_recipe_favorite", value=defaults["favorite"])
    st.text_area(
        "Descripcion",
        key=f"{widget_prefix}_recipe_description",
        value=defaults["description"],
        height=90,
        placeholder="Cuenta brevemente de que trata la receta.",
    )
    st.subheader("Ingredientes")
    ingredients_df = pd.DataFrame(defaults["ingredients"])
    edited_ingredients = st.data_editor(
        ingredients_df,
        key=f"{widget_prefix}_ingredients_editor",
        num_rows="dynamic",
        width="stretch",
        column_config={"quantity": "Cantidad", "ingredient_name": "Ingrediente"},
    )
    st.subheader("Pasos")
    steps_df = pd.DataFrame(
        [{"instruction": step} for step in defaults["steps"]] or [{"instruction": ""}]
    )
    edited_steps = st.data_editor(
        steps_df,
        key=f"{widget_prefix}_steps_editor",
        num_rows="dynamic",
        width="stretch",
        column_config={"instruction": "Paso"},
    )
    st.text_area(
        "Notas",
        key=f"{widget_prefix}_recipe_notes",
        value=defaults["notes"],
        height=85,
        placeholder="Consejos, trucos o recordatorios.",
    )
    uploaded_files = st.file_uploader(
        "Fotos de referencia",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        key=f"{widget_prefix}_recipe_images",
    )
    step_rows = edited_steps.get("instruction", pd.Series(dtype=str)).fillna("").tolist()
    return edited_ingredients.to_dict("records"), step_rows, uploaded_files


def recipe_image_or_placeholder(recipe: dict, key: str) -> None:
    if recipe["images"]:
        first_image = recipe["images"][0]
        if first_image.get("image_data_base64"):
            st.image(base64.b64decode(first_image["image_data_base64"]), width="stretch")
            return
        image_path = Path(first_image["file_path"])
        if image_path.exists():
            st.image(str(image_path), width="stretch")
            return
    st.markdown(f'<div class="recipe-thumb">{key}</div>', unsafe_allow_html=True)


def render_recipe_card(recipe: dict, button_key: str, emoji: str = "\U0001F372") -> None:
    st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
    recipe_image_or_placeholder(recipe, emoji)
    st.markdown('<div class="recipe-body">', unsafe_allow_html=True)
    st.markdown(f'<p class="recipe-title">{recipe["name"]}</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="recipe-soft">{recipe["category"] or "Sin categoria"} | {recipe["prep_time_minutes"] or 0} min</p>',
        unsafe_allow_html=True,
    )
    if recipe["favorite"]:
        st.markdown('<span class="mini-chip">Favorita</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="mini-chip">{recipe["difficulty"]}</span>', unsafe_allow_html=True)
    if st.button("Abrir", key=button_key):
        open_recipe_detail(recipe["id"])
        st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)


def build_full_recipe_list() -> list[dict]:
    recipes = []
    for summary in list_recipes():
        full_recipe = get_recipe(summary["id"])
        if full_recipe:
            recipes.append(full_recipe)
    return recipes


def render_home(recipes: list[dict], favorites: list[dict]) -> None:
    show_flash_message()
    st.markdown(
        f"""
        <div class="app-top">
            <div>
                <p class="hello-title">{greeting_text()}</p>
                <p class="hello-subtitle">Encuentra una receta facil para hoy.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="search-block">', unsafe_allow_html=True)
    with st.form("home_search_form", clear_on_submit=False):
        st.text_input("Buscar", key="home_search", label_visibility="collapsed", placeholder="Busca por nombre o ingrediente")
        st.form_submit_button("Filtrar")
    st.markdown("</div>", unsafe_allow_html=True)

    icons = [
        ("\U0001F951", "Aguacate"),
        ("\U0001F95A", "Huevo"),
        ("\U0001F969", "Carne"),
        ("\U0001F96C", "Verdura"),
        ("\U0001F35A", "Arroz"),
    ]
    cols = st.columns(5)
    for index, (emoji, label) in enumerate(icons):
        with cols[index]:
            st.markdown(
                f"""
                <div class="category-chip">
                    <div class="category-circle">{emoji}</div>
                    <div class="category-text">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    search_key = st.session_state.home_search.strip().lower()
    filtered = recipes
    if search_key:
        filtered = [
            recipe
            for recipe in recipes
            if search_key in recipe["name"].lower()
            or search_key in recipe["description"].lower()
            or any(search_key in ingredient["ingredient_name"].lower() for ingredient in recipe["ingredients"])
        ]
    if not recipes:
        st.info("Todavia no hay recetas guardadas.")
        return
    if search_key and not filtered:
        st.warning("No encontramos recetas con esa busqueda.")
        return

    st.markdown('<p class="section-title">Nuevas Recetas</p>', unsafe_allow_html=True)
    new_cols = st.columns(2)
    for index, recipe in enumerate(filtered[:2]):
        with new_cols[index % 2]:
            render_recipe_card(recipe, f"home_new_{recipe['id']}", "\U0001F35D")

    st.markdown('<p class="section-title">Recetas destacadas</p>', unsafe_allow_html=True)
    video_cols = st.columns(2)
    video_recipes = filtered[2:4] if len(filtered) > 2 else filtered[:2]
    for index, recipe in enumerate(video_recipes):
        with video_cols[index % 2]:
            render_recipe_card(recipe, f"home_video_{recipe['id']}", "\u25B6")

    st.markdown('<p class="section-title">Favoritas</p>', unsafe_allow_html=True)
    community_cols = st.columns(2)
    community_recipes = favorites[:2] if favorites else filtered[:2]
    for index, recipe in enumerate(community_recipes):
        with community_cols[index % 2]:
            render_recipe_card(recipe, f"home_community_{recipe['id']}", "\U0001F957")

    st.markdown('<p class="section-title">Todas tus recetas</p>', unsafe_allow_html=True)
    all_cols = st.columns(2)
    for index, recipe in enumerate(filtered):
        with all_cols[index % 2]:
            render_recipe_card(recipe, f"home_all_{recipe['id']}", "\U0001F37D")


def render_detail(recipe: dict) -> None:
    top_cols = st.columns([1, 4])
    with top_cols[0]:
        if st.button("<", key="detail_back"):
            close_recipe_detail()
            st.rerun()
    with top_cols[1]:
        st.markdown('<p class="section-title">Receta</p>', unsafe_allow_html=True)

    st.markdown('<div class="detail-hero">', unsafe_allow_html=True)
    recipe_image_or_placeholder(recipe, "\U0001F37D")
    st.markdown(f'<p class="detail-title">{recipe["name"]}</p>', unsafe_allow_html=True)
    if recipe["description"]:
        st.caption(recipe["description"])
    st.markdown(
        f"""
        <div class="stats-row">
            <div class="stat-pill"><strong>{len(recipe["ingredients"])}</strong><span>Ingredientes</span></div>
            <div class="stat-pill"><strong>{recipe["difficulty"]}</strong><span>Dificultad</span></div>
            <div class="stat-pill"><strong>{recipe["prep_time_minutes"] or 0} min</strong><span>Tiempo</span></div>
            <div class="stat-pill"><strong>{recipe["servings"] or 0}</strong><span>Porciones</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.radio(
        "Detalle",
        ["Ingredientes", "Pasos", "Trucos"],
        key="detail_view",
        horizontal=True,
        label_visibility="collapsed",
    )

    if st.session_state.detail_view == "Ingredientes":
        for ingredient in recipe["ingredients"]:
            amount = ingredient["quantity"] or "Al gusto"
            st.markdown(
                f"""
                <div class="ingredient-card">
                    <strong>{ingredient["ingredient_name"]}</strong><br>
                    <span class="recipe-soft">{amount}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    elif st.session_state.detail_view == "Pasos":
        for step in recipe["steps"]:
            st.markdown(
                f"""
                <div class="step-card">
                    <span class="step-number">{step["step_number"]}</span>
                    {step["instruction"]}
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        if recipe["notes"]:
            st.markdown(f'<div class="ingredient-card">{recipe["notes"]}</div>', unsafe_allow_html=True)
        else:
            st.info("Esta receta aun no tiene consejos extra.")


def render_add() -> None:
    st.markdown('<p class="section-title">Agregar receta</p>', unsafe_allow_html=True)
    show_flash_message()
    new_widget_prefix = f"new_{st.session_state.new_form_version}"
    with st.form(f"{new_widget_prefix}_form", clear_on_submit=False):
        ingredient_rows, step_rows, uploaded_files = render_editor(new_widget_prefix, get_recipe_defaults())
        save_col, reset_col = st.columns(2)
        with save_col:
            save_recipe = st.form_submit_button("Guardar receta")
        with reset_col:
            clear_recipe = st.form_submit_button("Limpiar formulario")
    if save_recipe:
        try:
            payload = payload_from_editor(new_widget_prefix, ingredient_rows, step_rows)
            create_recipe(payload, uploaded_files)
            reset_new_recipe_form()
            set_flash_message("La receta se guardo correctamente.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
    if clear_recipe:
        reset_new_recipe_form()
        st.rerun()


def render_search() -> None:
    st.markdown('<p class="section-title">Buscar recetas</p>', unsafe_allow_html=True)
    with st.form("search_form", clear_on_submit=False):
        st.text_input("Buscar por nombre o ingrediente", key="search_term", placeholder="Sopa, pollo, arroz...")
        st.selectbox("Categoria", ["Todas"] + get_categories(), key="search_category")
        st.checkbox("Solo favoritas", key="search_only_favorites")
        st.form_submit_button("Buscar recetas")
    search_term = st.session_state.get("search_term", "")
    category = st.session_state.get("search_category", "Todas")
    only_favorites = st.session_state.get("search_only_favorites", False)
    results = list_recipes(search_term, category)
    if only_favorites:
        results = [recipe for recipe in results if recipe["favorite"]]
    full_results = [get_recipe(recipe["id"]) for recipe in results]
    full_results = [recipe for recipe in full_results if recipe]
    if not full_results:
        st.info("No encontramos recetas con esos filtros.")
        return
    cols = st.columns(2)
    for index, recipe in enumerate(full_results):
        with cols[index % 2]:
            render_recipe_card(recipe, f"search_{recipe['id']}", "\U0001F35B")


def render_pantry() -> None:
    st.markdown('<p class="section-title">Mi cocina</p>', unsafe_allow_html=True)
    with st.form("pantry_form", clear_on_submit=False):
        st.multiselect(
            "Ingredientes que ya tienes",
            get_all_known_ingredients(),
            key="pantry_known_ingredients",
            placeholder="Selecciona o escribe ingredientes",
        )
        st.text_area(
            "Otros ingredientes",
            key="pantry_extra_ingredients",
            height=90,
            placeholder="Ejemplo: pollo, crema, cebolla",
        )
        st.form_submit_button("Buscar opciones")
    selected_known_ingredients = st.session_state.get("pantry_known_ingredients", [])
    extra_ingredients = st.session_state.get("pantry_extra_ingredients", "")
    pantry_items = [
        item.strip()
        for item in selected_known_ingredients + extra_ingredients.replace("\n", ",").split(",")
        if item.strip()
    ]
    if not pantry_items:
        st.info("Agrega ingredientes para ver sugerencias.")
        return
    suggestions = get_pantry_suggestions(pantry_items)
    if not suggestions:
        st.warning("Aun no encontramos recetas con esos ingredientes.")
        return
    for suggestion in suggestions:
        recipe = suggestion["recipe"]
        render_recipe_card(recipe, f'pantry_{recipe["id"]}', "\U0001F9FA")
        if suggestion["can_make_now"]:
            st.success("Puedes prepararla con lo que tienes.")
        else:
            st.caption("Te falta: " + ", ".join(suggestion["missing_ingredients"]))


def render_manage() -> None:
    st.markdown('<p class="section-title">Editar recetas</p>', unsafe_allow_html=True)
    show_flash_message()
    options = {recipe["name"]: recipe["id"] for recipe in list_recipes()}
    selected_name = st.selectbox("Selecciona una receta", [""] + list(options.keys()))
    if not selected_name:
        st.info("Elige una receta para editarla.")
        return
    selected_recipe = get_recipe(options[selected_name])
    if not selected_recipe:
        return
    edit_prefix = f'edit_{selected_recipe["id"]}'
    with st.form(f"{edit_prefix}_form", clear_on_submit=False):
        edit_ingredients, edit_steps, new_images = render_editor(edit_prefix, get_recipe_defaults(selected_recipe))
        replace_images = st.checkbox("Reemplazar imagenes actuales", key=f"{edit_prefix}_replace_images")
        save_changes = st.form_submit_button("Guardar cambios")
    if save_changes:
        try:
            payload = payload_from_editor(edit_prefix, edit_ingredients, edit_steps)
            update_recipe(selected_recipe["id"], payload, new_images, replace_images=replace_images)
            set_flash_message("La receta se actualizo correctamente.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
    if st.button("Eliminar receta", key="delete_recipe_button"):
        delete_recipe(selected_recipe["id"])
        set_flash_message("La receta fue eliminada.", "warning")
        st.rerun()


def render_share() -> None:
    st.markdown('<p class="section-title">Compartir</p>', unsafe_allow_html=True)
    st.info("Aqui veras una guia rapida para abrir la app desde cualquier celular.")
    with st.expander("Como verla desde otro movil con internet"):
        st.write("1. Sube esta carpeta a GitHub.")
        st.write("2. Entra a Streamlit Community Cloud.")
        st.write("3. Selecciona este proyecto y agrega el secreto DATABASE_URL.")
        st.write("4. Publica y usa el enlace generado.")


ensure_state()
apply_theme(st.session_state.theme)

full_recipes = build_full_recipe_list()
favorite_recipes = [recipe for recipe in full_recipes if recipe["favorite"]]
selected_recipe = get_recipe(st.session_state.selected_recipe_id) if st.session_state.selected_recipe_id else None

st.markdown('<div class="phone-shell">', unsafe_allow_html=True)

top_theme_col, top_stats_col = st.columns([2, 3])
with top_theme_col:
    st.radio("Tema", ["Claro", "Oscuro"], key="theme", horizontal=True, label_visibility="collapsed")
with top_stats_col:
    stats = get_dashboard_stats()
    st.caption(f'{stats["recipes"]} recetas | {stats["favorites"]} favoritas | {stats["ingredients"]} ingredientes')

if st.session_state.pending_section:
    st.session_state.current_section = st.session_state.pending_section
    st.session_state.nav_choice = st.session_state.pending_section
    st.session_state.pending_section = None

sections = ["Recetas", "Mi cocina", "Agregar", "Administrar", "Compartir"]
if st.session_state.current_section == "Detalle":
    sections = ["Detalle"] + sections
if st.session_state.nav_choice not in sections:
    st.session_state.nav_choice = sections[0]
active_section = st.radio("Navegacion", sections, key="nav_choice", horizontal=True, label_visibility="collapsed")
st.session_state.current_section = active_section

st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)

if active_section == "Detalle":
    if selected_recipe:
        render_detail(selected_recipe)
    else:
        close_recipe_detail()
        st.rerun()
elif active_section == "Recetas":
    render_home(full_recipes, favorite_recipes)
elif active_section == "Mi cocina":
    render_pantry()
elif active_section == "Agregar":
    render_add()
elif active_section == "Administrar":
    render_manage()
else:
    render_share()

st.markdown("</div>", unsafe_allow_html=True)
