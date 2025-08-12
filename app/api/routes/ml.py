from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from functools import lru_cache
from pathlib import Path
import pandas as pd
import mlflow
import os

router = APIRouter(prefix="/ml", tags=["ml"])

# IMPORTANT: ordre identique à l'entraînement (X = data.drop(["date","demand"]))
FEATURES = [
    "average_temperature",
    "rainfall",
    "weekend",
    "holiday",
    "price_per_kg",
    "promo",
    "previous_days_demand",
]

class PredictPayload(BaseModel):
    average_temperature: float
    rainfall: float
    weekend: int
    holiday: int
    price_per_kg: float
    promo: int
    previous_days_demand: float

@lru_cache
def load_model():
    # 1) si défini, on prend la variable d'env (Render > Environment > MODEL_URI)
    model_uri = os.getenv("MODEL_URI")
    if not model_uri:
        # 2) sinon, calcul sûr: /app (racine repo) = parents[3] depuis app/api/routes/ml.py
        project_root = Path(__file__).resolve().parents[3]   # -> /app
        model_uri = str(project_root / "rf_apples")          # -> /app/rf_apples

    try:
        return mlflow.sklearn.load_model(model_uri)
    except Exception as e:
        raise RuntimeError(f"Failed to load model from '{model_uri}': {e}")

@router.get("/ping")
def ping():
    return {"status": "ok"}

@router.post("/predict")
def predict(p: PredictPayload):
    model = load_model()
    X = pd.DataFrame([[getattr(p, f) for f in FEATURES]], columns=FEATURES)
    try:
        y = model.predict(X)
        return {"prediction": float(y[0])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
