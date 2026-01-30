from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field

# ------------------------------------------------------------
# Constantes métiers : une seule source de vérité
# (tickets.py peut réutiliser ces constantes)
# ------------------------------------------------------------
ALLOWED_PRIORITY = {"Low", "Medium", "High"}
ALLOWED_STATUS = {"Open", "In progress", "Closed"}

# Limites anti-champs "infinis" (ajuste si besoin)
MAX_TITLE_LEN = 120
MAX_DESC_LEN = 2000
MAX_TAGS = 20
MAX_TAG_LEN = 30


# ------------------------------------------------------------
# Compat Pydantic v1/v2 pour les validators
# ------------------------------------------------------------
try:
    # Pydantic v2
    from pydantic import field_validator as _validator
except Exception:
    # Pydantic v1
    from pydantic import validator as _validator


def _clean_text(v: str) -> str:
    """Nettoie une string: strip + refuse vide."""
    if not isinstance(v, str):
        raise ValueError("Doit être une chaîne de caractères.")
    v = v.strip()
    if not v:
        raise ValueError("Ne peut pas être vide.")
    return v


def _clean_tags(tags: Optional[List[str]]) -> List[str]:
    """Nettoie tags: liste, max, strip, supprime vides, longueur max."""
    if tags is None:
        return []

    if not isinstance(tags, list):
        raise ValueError("tags doit être une liste de chaînes.")

    if len(tags) > MAX_TAGS:
        raise ValueError(f"Maximum {MAX_TAGS} tags autorisés.")

    cleaned: List[str] = []
    for t in tags:
        if not isinstance(t, str):
            raise ValueError("Chaque tag doit être une chaîne.")
        tt = t.strip()
        if not tt:
            continue
        if len(tt) > MAX_TAG_LEN:
            raise ValueError(f"Un tag ne doit pas dépasser {MAX_TAG_LEN} caractères.")
        cleaned.append(tt)

    return cleaned


# ------------------------------------------------------------
# Modèles
# ------------------------------------------------------------
class TicketCreate(BaseModel):
    """
    Ce que le client DOIT envoyer pour créer un ticket.
    """

    title: str = Field(..., min_length=1, max_length=MAX_TITLE_LEN)
    description: str = Field(..., min_length=1, max_length=MAX_DESC_LEN)

    priority: str = Field(default="Low", description="Low | Medium | High")
    status: str = Field(default="Open", description="Open | In progress | Closed")

    tags: List[str] = Field(default_factory=list, description="Liste de tags (ex: bug, ui, backend)")

    # --- Validations ---
    @_validator("title")
    def validate_title(cls, v: str):
        return _clean_text(v)

    @_validator("description")
    def validate_description(cls, v: str):
        return _clean_text(v)

    @_validator("priority")
    def validate_priority(cls, v: str):
        if v not in ALLOWED_PRIORITY:
            raise ValueError(f"Priorité invalide. Valeurs possibles: {sorted(ALLOWED_PRIORITY)}")
        return v

    @_validator("status")
    def validate_status(cls, v: str):
        if v not in ALLOWED_STATUS:
            raise ValueError(f"Statut invalide. Valeurs possibles: {sorted(ALLOWED_STATUS)}")
        return v

    @_validator("tags")
    def validate_tags(cls, tags: List[str]):
        return _clean_tags(tags)


class TicketUpdate(BaseModel):
    """
    Ce que le client PEUT envoyer pour modifier (PATCH).
    Tous les champs sont optionnels.
    """

    title: Optional[str] = Field(default=None, min_length=1, max_length=MAX_TITLE_LEN)
    description: Optional[str] = Field(default=None, min_length=1, max_length=MAX_DESC_LEN)

    status: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None  # si tu veux autoriser patch tags

    # --- Validations ---
    @_validator("title")
    def validate_title_optional(cls, v):
        if v is None:
            return v
        return _clean_text(v)

    @_validator("description")
    def validate_description_optional(cls, v):
        if v is None:
            return v
        return _clean_text(v)

    @_validator("priority")
    def validate_priority_optional(cls, v):
        if v is None:
            return v
        if v not in ALLOWED_PRIORITY:
            raise ValueError(f"Priorité invalide. Valeurs possibles: {sorted(ALLOWED_PRIORITY)}")
        return v

    @_validator("status")
    def validate_status_optional(cls, v):
        if v is None:
            return v
        if v not in ALLOWED_STATUS:
            raise ValueError(f"Statut invalide. Valeurs possibles: {sorted(ALLOWED_STATUS)}")
        return v

    @_validator("tags")
    def validate_tags_optional(cls, tags):
        if tags is None:
            return tags
        return _clean_tags(tags)


def payload_to_dict(payload: TicketUpdate) -> Dict[str, Any]:
    """
    Convertit l'objet Pydantic en dict.
    exclude_unset=True = ne garde que les champs réellement envoyés.
    """
    if hasattr(payload, "model_dump"):  # Pydantic v2
        return payload.model_dump(exclude_unset=True)
    return payload.dict(exclude_unset=True)  # Pydantic v1
