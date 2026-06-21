from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from sqlalchemy import exc, text

from recipe_app.db import IMAGES_DIR, get_connection, init_db, is_postgres


@dataclass
class RecipePayload:
    name: str
    description: str
    category: str
    prep_time_minutes: int
    servings: int
    difficulty: str
    notes: str
    favorite: bool
    ingredients: list[dict[str, str]]
    steps: list[str]


def row_to_dict(row) -> dict:
    return dict(row._mapping)


def rows_to_dicts(rows) -> list[dict]:
    return [row_to_dict(row) for row in rows]


def normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


def clean_ingredients(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    cleaned = []
    for row in rows:
        quantity = str(row.get("quantity", "") or "").strip()
        name = str(row.get("ingredient_name", "") or "").strip()
        if not name:
            continue
        cleaned.append(
            {
                "ingredient_name": name,
                "ingredient_key": normalize_text(name),
                "quantity": quantity,
            }
        )
    return cleaned


def clean_steps(steps: Iterable[str]) -> list[str]:
    return [step.strip() for step in steps if str(step).strip()]


def validate_payload(payload: RecipePayload) -> None:
    if not payload.name.strip():
        raise ValueError("La receta necesita un nombre.")
    if not payload.ingredients:
        raise ValueError("Agrega al menos un ingrediente.")
    if not payload.steps:
        raise ValueError("Agrega al menos un paso de preparacion.")


def save_uploaded_images(uploaded_files: Iterable) -> list[dict[str, str]]:
    saved_images: list[dict[str, str]] = []
    for uploaded_file in uploaded_files or []:
        extension = Path(uploaded_file.name).suffix or ".jpg"
        filename = f"{datetime.now():%Y%m%d%H%M%S}_{uuid4().hex}{extension}"
        file_path = IMAGES_DIR / filename
        file_path.write_bytes(uploaded_file.getbuffer())
        saved_images.append(
            {
                "file_path": str(file_path),
                "original_name": uploaded_file.name,
            }
        )
    return saved_images


def cleanup_saved_images(saved_images: Iterable[dict[str, str]]) -> None:
    for image in saved_images:
        image_path = Path(image["file_path"])
        if image_path.exists():
            image_path.unlink()


def create_recipe(payload: RecipePayload, uploaded_files: Iterable | None = None) -> int:
    validate_payload(payload)
    image_rows = save_uploaded_images(uploaded_files or [])
    try:
        with get_connection() as connection:
            recipe_id = connection.execute(
                text(
                    """
                    INSERT INTO recipes (
                        name, description, category, prep_time_minutes,
                        servings, difficulty, notes, favorite, updated_at
                    )
                    VALUES (
                        :name, :description, :category, :prep_time_minutes,
                        :servings, :difficulty, :notes, :favorite, CURRENT_TIMESTAMP
                    )
                    RETURNING id
                    """
                ),
                {
                    "name": payload.name.strip(),
                    "description": payload.description.strip(),
                    "category": payload.category.strip(),
                    "prep_time_minutes": payload.prep_time_minutes,
                    "servings": payload.servings,
                    "difficulty": payload.difficulty.strip(),
                    "notes": payload.notes.strip(),
                    "favorite": payload.favorite if is_postgres() else int(payload.favorite),
                },
            ).scalar_one()

            connection.execute(
                text(
                    """
                    INSERT INTO recipe_ingredients (recipe_id, ingredient_name, ingredient_key, quantity)
                    VALUES (:recipe_id, :ingredient_name, :ingredient_key, :quantity)
                    """
                ),
                [
                    {
                        "recipe_id": recipe_id,
                        "ingredient_name": ingredient["ingredient_name"],
                        "ingredient_key": ingredient["ingredient_key"],
                        "quantity": ingredient["quantity"],
                    }
                    for ingredient in payload.ingredients
                ],
            )

            connection.execute(
                text(
                    """
                    INSERT INTO recipe_steps (recipe_id, step_number, instruction)
                    VALUES (:recipe_id, :step_number, :instruction)
                    """
                ),
                [
                    {
                        "recipe_id": recipe_id,
                        "step_number": step_number,
                        "instruction": instruction,
                    }
                    for step_number, instruction in enumerate(payload.steps, start=1)
                ],
            )

            if image_rows:
                connection.execute(
                    text(
                        """
                        INSERT INTO recipe_images (recipe_id, file_path, original_name)
                        VALUES (:recipe_id, :file_path, :original_name)
                        """
                    ),
                    [
                        {
                            "recipe_id": recipe_id,
                            "file_path": image["file_path"],
                            "original_name": image["original_name"],
                        }
                        for image in image_rows
                    ],
                )
    except exc.IntegrityError as error:
        cleanup_saved_images(image_rows)
        raise ValueError("Ya existe una receta con ese nombre. Usa otro nombre o edita la actual.") from error

    return int(recipe_id)


def update_recipe(
    recipe_id: int,
    payload: RecipePayload,
    uploaded_files: Iterable | None = None,
    replace_images: bool = False,
) -> None:
    validate_payload(payload)
    image_rows = save_uploaded_images(uploaded_files or [])
    try:
        with get_connection() as connection:
            connection.execute(
                text(
                    """
                    UPDATE recipes
                    SET name = :name,
                        description = :description,
                        category = :category,
                        prep_time_minutes = :prep_time_minutes,
                        servings = :servings,
                        difficulty = :difficulty,
                        notes = :notes,
                        favorite = :favorite,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :recipe_id
                    """
                ),
                {
                    "recipe_id": recipe_id,
                    "name": payload.name.strip(),
                    "description": payload.description.strip(),
                    "category": payload.category.strip(),
                    "prep_time_minutes": payload.prep_time_minutes,
                    "servings": payload.servings,
                    "difficulty": payload.difficulty.strip(),
                    "notes": payload.notes.strip(),
                    "favorite": payload.favorite if is_postgres() else int(payload.favorite),
                },
            )

            connection.execute(text("DELETE FROM recipe_ingredients WHERE recipe_id = :recipe_id"), {"recipe_id": recipe_id})
            connection.execute(text("DELETE FROM recipe_steps WHERE recipe_id = :recipe_id"), {"recipe_id": recipe_id})

            connection.execute(
                text(
                    """
                    INSERT INTO recipe_ingredients (recipe_id, ingredient_name, ingredient_key, quantity)
                    VALUES (:recipe_id, :ingredient_name, :ingredient_key, :quantity)
                    """
                ),
                [
                    {
                        "recipe_id": recipe_id,
                        "ingredient_name": ingredient["ingredient_name"],
                        "ingredient_key": ingredient["ingredient_key"],
                        "quantity": ingredient["quantity"],
                    }
                    for ingredient in payload.ingredients
                ],
            )
            connection.execute(
                text(
                    """
                    INSERT INTO recipe_steps (recipe_id, step_number, instruction)
                    VALUES (:recipe_id, :step_number, :instruction)
                    """
                ),
                [
                    {
                        "recipe_id": recipe_id,
                        "step_number": step_number,
                        "instruction": instruction,
                    }
                    for step_number, instruction in enumerate(payload.steps, start=1)
                ],
            )

            if replace_images:
                old_images = rows_to_dicts(
                    connection.execute(
                        text("SELECT file_path FROM recipe_images WHERE recipe_id = :recipe_id"),
                        {"recipe_id": recipe_id},
                    ).fetchall()
                )
                connection.execute(text("DELETE FROM recipe_images WHERE recipe_id = :recipe_id"), {"recipe_id": recipe_id})
                for image in old_images:
                    image_path = Path(image["file_path"])
                    if image_path.exists():
                        image_path.unlink()

            if image_rows:
                connection.execute(
                    text(
                        """
                        INSERT INTO recipe_images (recipe_id, file_path, original_name)
                        VALUES (:recipe_id, :file_path, :original_name)
                        """
                    ),
                    [
                        {
                            "recipe_id": recipe_id,
                            "file_path": image["file_path"],
                            "original_name": image["original_name"],
                        }
                        for image in image_rows
                    ],
                )
    except exc.IntegrityError as error:
        cleanup_saved_images(image_rows)
        raise ValueError("Ya existe otra receta con ese nombre. Elige un nombre distinto.") from error


def delete_recipe(recipe_id: int) -> None:
    with get_connection() as connection:
        image_rows = rows_to_dicts(
            connection.execute(
                text("SELECT file_path FROM recipe_images WHERE recipe_id = :recipe_id"),
                {"recipe_id": recipe_id},
            ).fetchall()
        )
        connection.execute(text("DELETE FROM recipes WHERE id = :recipe_id"), {"recipe_id": recipe_id})

    for image in image_rows:
        image_path = Path(image["file_path"])
        if image_path.exists():
            image_path.unlink()


def list_recipes(search_term: str = "", category: str = "") -> list[dict]:
    filters = []
    params: dict[str, str] = {}

    if search_term.strip():
        filters.append("(LOWER(r.name) LIKE :wildcard OR LOWER(COALESCE(ri.ingredient_name, '')) LIKE :wildcard)")
        params["wildcard"] = f"%{search_term.strip().lower()}%"

    if category.strip() and category.strip() != "Todas":
        filters.append("r.category = :category")
        params["category"] = category.strip()

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    with get_connection() as connection:
        rows = connection.execute(
            text(
                f"""
                SELECT DISTINCT
                    r.id,
                    r.name,
                    r.description,
                    r.category,
                    r.prep_time_minutes,
                    r.servings,
                    r.difficulty,
                    r.notes,
                    r.favorite,
                    r.created_at,
                    r.updated_at
                FROM recipes r
                LEFT JOIN recipe_ingredients ri ON ri.recipe_id = r.id
                {where_clause}
                ORDER BY r.favorite DESC, r.updated_at DESC, r.name ASC
                """
            ),
            params,
        ).fetchall()
    return rows_to_dicts(rows)


def get_recipe(recipe_id: int) -> dict | None:
    with get_connection() as connection:
        recipe_row = connection.execute(
            text(
                """
                SELECT id, name, description, category, prep_time_minutes, servings,
                       difficulty, notes, favorite, created_at, updated_at
                FROM recipes
                WHERE id = :recipe_id
                """
            ),
            {"recipe_id": recipe_id},
        ).fetchone()
        if recipe_row is None:
            return None

        ingredients = connection.execute(
            text(
                """
                SELECT ingredient_name, ingredient_key, quantity
                FROM recipe_ingredients
                WHERE recipe_id = :recipe_id
                ORDER BY ingredient_name ASC
                """
            ),
            {"recipe_id": recipe_id},
        ).fetchall()
        steps = connection.execute(
            text(
                """
                SELECT step_number, instruction
                FROM recipe_steps
                WHERE recipe_id = :recipe_id
                ORDER BY step_number ASC
                """
            ),
            {"recipe_id": recipe_id},
        ).fetchall()
        images = connection.execute(
            text(
                """
                SELECT id, file_path, original_name
                FROM recipe_images
                WHERE recipe_id = :recipe_id
                ORDER BY id ASC
                """
            ),
            {"recipe_id": recipe_id},
        ).fetchall()

    recipe_dict = row_to_dict(recipe_row)
    recipe_dict["ingredients"] = rows_to_dicts(ingredients)
    recipe_dict["steps"] = rows_to_dicts(steps)
    recipe_dict["images"] = rows_to_dicts(images)
    return recipe_dict


def get_categories() -> list[str]:
    with get_connection() as connection:
        rows = connection.execute(
            text(
                """
                SELECT DISTINCT category
                FROM recipes
                WHERE TRIM(category) <> ''
                ORDER BY category ASC
                """
            )
        ).fetchall()
    return [row_to_dict(row)["category"] for row in rows]


def get_all_known_ingredients() -> list[str]:
    with get_connection() as connection:
        rows = connection.execute(
            text(
                """
                SELECT DISTINCT ingredient_name
                FROM recipe_ingredients
                ORDER BY ingredient_name ASC
                """
            )
        ).fetchall()
    return [row_to_dict(row)["ingredient_name"] for row in rows]


def get_dashboard_stats() -> dict[str, int]:
    with get_connection() as connection:
        recipes_count = connection.execute(text("SELECT COUNT(*) AS total FROM recipes")).scalar_one()
        ingredients_count = connection.execute(
            text("SELECT COUNT(DISTINCT ingredient_key) AS total FROM recipe_ingredients")
        ).scalar_one()
        favorites_count = connection.execute(
            text("SELECT COUNT(*) AS total FROM recipes WHERE favorite = :favorite"),
            {"favorite": True if is_postgres() else 1},
        ).scalar_one()
    return {
        "recipes": int(recipes_count),
        "ingredients": int(ingredients_count),
        "favorites": int(favorites_count),
    }


def get_pantry_suggestions(pantry_items: Iterable[str]) -> list[dict]:
    pantry_keys = {normalize_text(item) for item in pantry_items if normalize_text(item)}
    suggestions: list[dict] = []

    for recipe in list_recipes():
        full_recipe = get_recipe(recipe["id"])
        if not full_recipe:
            continue

        ingredient_keys = {ingredient["ingredient_key"] for ingredient in full_recipe["ingredients"]}
        total = len(ingredient_keys)
        matched = len(ingredient_keys & pantry_keys)
        missing = [
            ingredient["ingredient_name"]
            for ingredient in full_recipe["ingredients"]
            if ingredient["ingredient_key"] not in pantry_keys
        ]
        suggestions.append(
            {
                "recipe": full_recipe,
                "total_ingredients": total,
                "matched_ingredients": matched,
                "missing_ingredients": missing,
                "can_make_now": len(missing) == 0 and total > 0,
                "match_percentage": round((matched / total) * 100) if total else 0,
            }
        )

    suggestions = [item for item in suggestions if item["matched_ingredients"] > 0]
    suggestions.sort(
        key=lambda item: (
            not item["can_make_now"],
            len(item["missing_ingredients"]),
            -item["matched_ingredients"],
            item["recipe"]["name"].lower(),
        )
    )
    return suggestions


def seed_sample_data() -> None:
    init_db()
    with get_connection() as connection:
        current_count = connection.execute(text("SELECT COUNT(*) AS total FROM recipes")).scalar_one()
        if int(current_count) > 0:
            return

    create_recipe(
        RecipePayload(
            name="Pasta con tomate y albahaca",
            description="Una receta rapida, fresca y facil para almuerzo o cena.",
            category="Almuerzo",
            prep_time_minutes=25,
            servings=2,
            difficulty="Facil",
            notes="Puedes agregar queso rallado al servir.",
            favorite=True,
            ingredients=clean_ingredients(
                [
                    {"quantity": "250 g", "ingredient_name": "Pasta"},
                    {"quantity": "4", "ingredient_name": "Tomates"},
                    {"quantity": "2 dientes", "ingredient_name": "Ajo"},
                    {"quantity": "8 hojas", "ingredient_name": "Albahaca"},
                    {"quantity": "2 cucharadas", "ingredient_name": "Aceite de oliva"},
                ]
            ),
            steps=clean_steps(
                [
                    "Hervir la pasta en agua con sal hasta que quede al dente.",
                    "Sofreir el ajo con el aceite de oliva durante 1 minuto.",
                    "Agregar los tomates picados y cocinar hasta formar una salsa ligera.",
                    "Mezclar la pasta con la salsa y terminar con albahaca fresca.",
                ]
            ),
        )
    )

    create_recipe(
        RecipePayload(
            name="Omelette de vegetales",
            description="Ideal para desayunos o cenas ligeras con lo que tengas en casa.",
            category="Desayuno",
            prep_time_minutes=15,
            servings=1,
            difficulty="Facil",
            notes="Funciona bien con queso, cebolla o espinaca.",
            favorite=False,
            ingredients=clean_ingredients(
                [
                    {"quantity": "2", "ingredient_name": "Huevos"},
                    {"quantity": "1/4 taza", "ingredient_name": "Pimiento"},
                    {"quantity": "1/4 taza", "ingredient_name": "Cebolla"},
                    {"quantity": "1 cucharada", "ingredient_name": "Mantequilla"},
                    {"quantity": "Al gusto", "ingredient_name": "Sal"},
                ]
            ),
            steps=clean_steps(
                [
                    "Batir los huevos con sal.",
                    "Saltear cebolla y pimiento con mantequilla.",
                    "Agregar los huevos y cocinar a fuego bajo hasta que cuaje.",
                    "Doblar el omelette y servir caliente.",
                ]
            ),
        )
    )
