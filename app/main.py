from fastapi import FastAPI
from app.api.routes import entreprise, skills, OLAP, candidat,search, ml

app = FastAPI()

app.include_router(skills.router)
app.include_router(entreprise.router)
app.include_router(OLAP.router)
app.include_router(candidat.router)
app.include_router(search.router)
app.include_router(ml.router,     prefix="/api")