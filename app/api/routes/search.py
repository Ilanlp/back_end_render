from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime, timedelta
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
    contrat: Optional[List[str]] = Query(None),
    date_filter: Optional[str] = Query(None, description="last_24h | last_3_days | last_7_days"),
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0)
):
    # Conditions regroupées
    lieu_conditions = []
    other_conditions = []

    if ville:
        lieu_conditions.append(make_like_conditions("l.ville", ville))
    if departement:
        lieu_conditions.append(make_like_conditions("l.departement", departement))
    if region:
        lieu_conditions.append(make_like_conditions("l.region", region))
    if skill:
        other_conditions.append(f"({make_like_conditions('s.skill', skill)})")
    if contrat:
        other_conditions.append(f"({make_like_conditions('c.type_contrat', contrat)})")

    if date_filter:
        now = datetime.now()
        if date_filter == "last_24h":
            since_date = now - timedelta(days=1)
        elif date_filter == "last_3_days":
            since_date = now - timedelta(days=3)
        elif date_filter == "last_7_days":
            since_date = now - timedelta(days=7)
        else:
            return {"error": "Invalid value for date_filter"}
        other_conditions.append(f"o.id_date_creation >= '{since_date.date()}'")

    # WHERE clause
    clauses = []
    if lieu_conditions:
        clauses.append(f"({' OR '.join(lieu_conditions)})")
    if other_conditions:
        clauses.append(" AND ".join(other_conditions))
    where_clause = " AND ".join(clauses) if clauses else "TRUE"

    # Requête principale
    main_query = f"""
        SELECT DISTINCT o.id_offre, o.title, l.ville, l.region, o.source_url, c.type_contrat, 
               ARRAY_AGG(DISTINCT s.skill) AS skills
        FROM FAIT_OFFRE o
        JOIN DIM_LIEU l ON o.id_lieu = l.id_lieu
        LEFT JOIN LIAISON_OFFRE_COMPETENCE lc ON o.id_offre = lc.id_offre
        LEFT JOIN DIM_COMPETENCE s ON lc.id_competence = s.id_competence
        LEFT JOIN DIM_CONTRAT c ON o.id_contrat = c.id_contrat
        WHERE {where_clause}
        GROUP BY o.id_offre, o.title, l.ville, l.region, o.source_url, c.type_contrat
        LIMIT {limit} OFFSET {offset};
    """

    # Requête de comptage
    count_query = f"""
        SELECT COUNT(DISTINCT o.id_offre)
        FROM FAIT_OFFRE o
        JOIN DIM_LIEU l ON o.id_lieu = l.id_lieu
        LEFT JOIN LIAISON_OFFRE_COMPETENCE lc ON o.id_offre = lc.id_offre
        LEFT JOIN DIM_COMPETENCE s ON lc.id_competence = s.id_competence
        LEFT JOIN DIM_CONTRAT c ON o.id_contrat = c.id_contrat
        WHERE {where_clause};
    """

    try:
        data = queries.raw_query(main_query)
        total_result = queries.raw_query(count_query)
        print("💬 Résultat total_result:", repr(total_result))  # debug

        try:
            total_count = total_result[0]["COUNT(DISTINCT O.ID_OFFRE)"]
        except Exception as e:
            print("⚠️ Erreur dans total_count:", repr(e))
            total_count = 0


        return {
            "data": data,
            "total_count": total_count
        }
    except Exception as e:
        import traceback
        print("❌ ERREUR BACKEND :")
        traceback.print_exc()
        print("EXCEPTION VALUE:", repr(e))
        return {"error": str(e)}

