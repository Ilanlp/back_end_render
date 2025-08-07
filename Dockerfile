FROM python:3.11-slim

# Créer le dossier de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code source
COPY . .

# Exposer le port utilisé par uvicorn
EXPOSE 8000

# Commande de démarrage
CMD ["sh", "startup.sh"]
