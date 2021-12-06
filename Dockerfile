FROM python@sha256:03adad5f75b88bc36b4524feaa74d3726d77f7ef323654df619df5eb9225a843 AS build

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python@sha256:ab78639b9a19c806df52b44642e5e11ffd6ad01709c721b463fc78f474a18e84

WORKDIR /app

COPY --from=build /app/wheels /wheels
COPY --from=build /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY main.py rctf.py .

ENTRYPOINT ["python3", "/app/main.py"]
