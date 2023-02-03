FROM python:3.8-buster AS build

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.8-slim-buster

WORKDIR /app

COPY --from=build /app/wheels /wheels
COPY --from=build /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY main.py rctf.py .

ENTRYPOINT ["python3", "/app/main.py"]
