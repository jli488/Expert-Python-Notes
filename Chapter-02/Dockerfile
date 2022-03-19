FROM python:3.9-slim

ARG BUILD_ENV=development

WORKDIR /dev_env/

COPY requirements.txt poetry.lock pyproject.toml /dev_env/
RUN pip install -r requirements.txt && \
    poetry config virtualenvs.create false && \
    poetry install $(test "$BUILD_ENV" == "production" && echo "--no-dev") --no-interaction --no-ansi
