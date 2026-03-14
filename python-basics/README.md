`docker run -it --rm -v $(pwd)/python-basics:/app -w /app python:3.12-slim bash`

Das macht folgendes:
```
    -it                             → interaktives Terminal
    --rm                            → Container wird nach Exit gelöscht
    -v $(pwd)/python-basics:/app    → dein lokaler Ordner gemountet
    -w /app                         → Arbeitsverzeichnis im Container
    python:3.12-slim                → schlankes Python Image
```