FROM yamitzky/docker-python-rocksdb:latest

RUN mkdir -p /workers
ENV PYTHONPATH "$PYTHONPATH:/workers"
ENV PATH="${PATH}:/root/.poetry/bin"
WORKDIR /workers

RUN pip install --upgrade pip && pip install poetry
COPY pyproject.toml poetry.lock /workers/
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi --no-root
RUN rm /workers/pyproject.toml /workers/poetry.lock
