FROM registry.access.redhat.com/ubi9/python-312:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/

USER 0
RUN mkdir -p /app/uploads && \
    chgrp -R 0 /app && \
    chmod -R g=u /app

EXPOSE 8080

USER 1001

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--access-logfile", "-", "app:app"]
