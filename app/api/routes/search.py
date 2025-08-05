from fastapi import APIRouter, Query
from typing import List, Optional
from app.db import queries  # ta fonction raw_query doit être ici

router = APIRouter()

def make_like_conditions(column: str, values: List[str]) -> str:
    return " OR ".join([f"{column} ILIKE '%{val}%'" for val in values])

@router.get("/search")
def search_offres(
    skill: Optional[List[str]] = Query(None),
    ville: Optional[List[str]] = Query(None),
    departement: Optional[List[str]] = Query(None),
    region: Optional[List[str]] = Query(None),
    contrat: Optional[List[str]] = Query(None)
):
    conditions = []

    if ville:
        conditions.append(f"({make_like_conditions('l.ville', ville)})")
    if departement:
        conditions.append(f"({make_like_conditions('l.departement', departement)})")
    if region:
        conditions.append(f"({make_like_conditions('l.region', region)})")
    if skill:
        conditions.append(f"({make_like_conditions('s.skill', skill)})")
    if contrat:
        conditions.append(f"({make_like_conditions('c.type_contrat', contrat)})")

    where_clause = " AND ".join(conditions) if conditions else "TRUE"

    query = f"""
        SELECT DISTINCT o.id_offre, o.title, l.ville, l.region, o.source_url, c.type_contrat, ARRAY_AGG(DISTINCT s.skill) AS skills
        FROM FAIT_OFFRE o
        JOIN DIM_LIEU l ON o.id_lieu = l.id_lieu
        LEFT JOIN LIAISON_OFFRE_COMPETENCE lc ON o.id_offre = lc.id_offre
        LEFT JOIN DIM_COMPETENCE s ON lc.id_competence = s.id_competence
        LEFT JOIN DIM_CONTRAT c ON o.id_contrat  = c.id_contrat
        WHERE {where_clause}
        GROUP BY o.id_offre, o.title, l.ville, l.region, o.source_url, c.type_contrat;
    """

    try:
        results = queries.raw_query(query)
        return {"data": results}
    except Exception as e:
        return {"error": str(e)}
