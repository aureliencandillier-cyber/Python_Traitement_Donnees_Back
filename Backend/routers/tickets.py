from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any, List
from datetime import datetime

# ------------------------------------------------------------
# Imports robustes (package vs lancement direct)
# ------------------------------------------------------------
try:
    from ..models import (
        TicketCreate, TicketUpdate, payload_to_dict,
        ALLOWED_PRIORITY, ALLOWED_STATUS
    )
    from ..storage import load_tickets, save_tickets, next_id
except Exception:
    from models import (
        TicketCreate, TicketUpdate, payload_to_dict,
        ALLOWED_PRIORITY, ALLOWED_STATUS
    )
    from storage import load_tickets, save_tickets, next_id


router = APIRouter()

# Tri métier (évite "alphabétique")
PRIORITY_WEIGHT = {"Low": 1, "Medium": 2, "High": 3}
STATUS_WEIGHT = {"Open": 1, "In progress": 2, "Closed": 3}

ALLOWED_SORT_BY = {"id", "createdAt", "priority", "status", "title"}
ALLOWED_ORDER = {"asc", "desc"}


def parse_date_yyyy_mm_dd(value: str) -> datetime:
    """Parse YYYY-MM-DD. Si invalide, renvoie une date ancienne."""
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except Exception:
        return datetime(1970, 1, 1)


def normalize_tags(ticket: Dict[str, Any]) -> List[str]:
    """Retourne les tags du ticket en lowercase, sans crash si absent."""
    raw = ticket.get("tags") or []
    return [str(t).strip().lower() for t in raw if str(t).strip()]


def contains_text(ticket: Dict[str, Any], needle: str) -> bool:
    """
    Recherche insensible à la casse dans:
    - title
    - description
    - tags   ✅ (ça corrige ton test SECURITY qui retournait vide)
    """
    needle = needle.lower()

    hay_title = str(ticket.get("title", "")).lower()
    hay_desc = str(ticket.get("description", "")).lower()
    hay_tags = normalize_tags(ticket)

    return (
        needle in hay_title
        or needle in hay_desc
        or any(needle in t for t in hay_tags)
    )


def build_sort_key(field: str):
    """Retourne la key() adaptée au champ trié."""
    if field == "id":
        return lambda t: int(t.get("id", -1))
    if field == "title":
        return lambda t: str(t.get("title", "")).lower()
    if field == "createdAt":
        return lambda t: parse_date_yyyy_mm_dd(str(t.get("createdAt", "")))
    if field == "priority":
        return lambda t: PRIORITY_WEIGHT.get(t.get("priority"), 0)
    if field == "status":
        return lambda t: STATUS_WEIGHT.get(t.get("status"), 0)
    return lambda t: int(t.get("id", -1))


@router.get("/tickets")
def get_tickets(
    # ---------------- FILTRES ----------------
    status: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),

    # ---------------- TRI ----------------
    sort_by: str = Query(default="id"),
    order: str = Query(default="desc"),

    # ---------------- TRI SECONDAIRE ----------------
    then_by: Optional[str] = Query(default=None),
    then_order: str = Query(default="desc"),

    # ---------------- PAGINATION ----------------
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    tickets = load_tickets()

    # 1) Validations params
    if status is not None and status not in ALLOWED_STATUS:
        raise HTTPException(status_code=400, detail="Paramètre status invalide.")
    if priority is not None and priority not in ALLOWED_PRIORITY:
        raise HTTPException(status_code=400, detail="Paramètre priority invalide.")
    if sort_by not in ALLOWED_SORT_BY:
        raise HTTPException(status_code=400, detail="Paramètre sort_by invalide.")
    if order not in ALLOWED_ORDER:
        raise HTTPException(status_code=400, detail="Paramètre order invalide (asc/desc).")
    if then_by is not None and then_by not in ALLOWED_SORT_BY:
        raise HTTPException(status_code=400, detail="Paramètre then_by invalide.")
    if then_order not in ALLOWED_ORDER:
        raise HTTPException(status_code=400, detail="Paramètre then_order invalide (asc/desc).")

    # 2) Filtrage
    results = tickets

    if status is not None:
        results = [t for t in results if t.get("status") == status]

    if priority is not None:
        results = [t for t in results if t.get("priority") == priority]

    if tag is not None:
        tag_lc = tag.strip().lower()
        results = [t for t in results if tag_lc in normalize_tags(t)]

    if search is not None:
        needle = search.strip().lower()
        if needle:
            results = [t for t in results if contains_text(t, needle)]

    total = len(results)

    # 3) Tri multi-critères (stable)
    if then_by is not None:
        results.sort(key=build_sort_key(then_by), reverse=(then_order == "desc"))
    results.sort(key=build_sort_key(sort_by), reverse=(order == "desc"))

    # 4) Pagination
    paged = results[offset: offset + limit]

    return {
        "items": paged,
        "total": total,
        "limit": limit,
        "offset": offset,
        "sort_by": sort_by,
        "order": order,
        "then_by": then_by,
        "then_order": then_order,
        "filters": {"status": status, "priority": priority, "tag": tag, "search": search},
    }


@router.post("/tickets", status_code=201)
def create_ticket(payload: TicketCreate):
    """
    Ici on fait confiance à TicketCreate:
    - tailles max
    - strip
    - priority/status valides
    - tags propres
    """
    tickets = load_tickets()

    ticket = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    ticket["id"] = next_id(tickets)

    # Optionnel : auto date si absente
    if "createdAt" not in ticket:
        ticket["createdAt"] = datetime.now().strftime("%Y-%m-%d")

    tickets.append(ticket)
    save_tickets(tickets)
    return ticket


@router.patch("/tickets/{ticket_id}")
def patch_ticket(ticket_id: int, payload: TicketUpdate):
    """
    Idem : TicketUpdate gère les validations (si champ fourni).
    """
    tickets = load_tickets()

    ticket = next((t for t in tickets if int(t.get("id", -1)) == ticket_id), None)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ce ticket n'existe pas.")

    data = payload_to_dict(payload)
    if not data:
        raise HTTPException(status_code=400, detail="Aucune donnée reçue.")

    # applique les champs envoyés
    for k, v in data.items():
        ticket[k] = v

    save_tickets(tickets)
    return ticket


@router.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int):
    tickets = load_tickets()
    before = len(tickets)

    tickets = [t for t in tickets if int(t.get("id", -1)) != ticket_id]
    if len(tickets) == before:
        raise HTTPException(status_code=404, detail="Ticket introuvable.")

    save_tickets(tickets)
    return None
