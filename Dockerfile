FROM python:3.11-slim

WORKDIR /app

# Zainstaluj narzędzia systemowe
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Zainstaluj Poetry
RUN pip install poetry

# Konfiguracja Poetry
RUN poetry config virtualenvs.create false

# Kopiuj pliki projektu
COPY pyproject.toml poetry.lock* ./

# Zainstaluj zależności
RUN poetry install --no-interaction --no-ansi --no-root

# Kopiuj kod źródłowy
COPY . .

# Zainstaluj projekt
RUN poetry install --no-interaction --no-ansi

# Ustaw zmienne środowiskowe
ENV PYTHONPATH=/app
ENV OLLAMA_HOST=http://ollama:11434

# Domyślne polecenie
CMD ["python", "-m", "ollama_client.interfaces.shell.interactive"]