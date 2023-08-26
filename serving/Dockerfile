FROM tiangolo/uvicorn-gunicorn:python3.10

RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false && poetry install

COPY . /app/
