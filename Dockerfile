FROM mcr.microsoft.com/playwright:python

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium

COPY . .

ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
