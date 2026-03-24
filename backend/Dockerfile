FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
# ```

# Notice `COPY requirements.txt` and `RUN pip install` come **before** `COPY . .`. This is Docker layer caching. Docker caches each instruction. If you change `main.py`, Docker reuses the cached pip install layer — the rebuild takes 2 seconds instead of 45. If you put `COPY . .` first, every code change invalidates the cache and reinstalls all dependencies. This single ordering decision saves hours of waiting across a project.

# `requirements.txt` minimum for today:
# ```
# fastapi==0.111.0
# uvicorn[standard]==0.29.0
# celery==5.4.0
# redis==5.0.4
# psycopg2-binary==2.9.9
# python-dotenv==1.0.1