# Service de mise à jour, appelé par n8n sur le serveur.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends git openssh-client ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 updater
COPY server.py /app/server.py
USER updater
WORKDIR /work
EXPOSE 8080
CMD ["python", "-u", "/app/server.py"]
