FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --create-home --uid 10001 sasteratech
COPY requirements/runtime-lock.txt /tmp/runtime-lock.txt
RUN python -m pip install --no-cache-dir --require-hashes -r /tmp/runtime-lock.txt
COPY . /app
RUN chown -R sasteratech:sasteratech /app
USER sasteratech
CMD ["python", "scripts/run_birth_candidate.py", "--verify-only"]
