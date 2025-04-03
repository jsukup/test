FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run tests (can be commented out in production)
# RUN pytest -xvs tests/

EXPOSE 1983

CMD ["gunicorn", "--bind", "0.0.0.0:1983", "--access-logfile", "-", "--error-logfile", "-", "app:app"]