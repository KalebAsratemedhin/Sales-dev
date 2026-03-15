FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Chromium for LinkedIn session refresh (Selenium/undetected-chromedriver)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    chromium \
    libnss3 \
    libgbm1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libdrm2 \
    libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*

ENV LINKEDIN_CHROME_PATH=/usr/bin/chromium

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "config.wsgi:application"]