<div align="center">
  <h1>WTTJ Job Bot</h1>
  <p>
    <strong>Automate your job hunt on Welcome to the Jungle</strong>
  </p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white"/>
    <img src="https://img.shields.io/badge/Playwright-45BA4B?style=flat-square&logo=playwright&logoColor=white"/>
    <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white"/>
    <img src="https://github.com/Bfault/wttj-job-bot/actions/workflows/ci.yml/badge.svg"/>
    <img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square"/>
  </p>
</div>

---

## ✨ Features

- **Scrape** — find companies hiring on WTTJ by keyword, filter by region, exclude blacklisted names
- **Apply** — send spontaneous applications with a custom cover letter automatically
- **Deduplicated** — same company won't appear twice across multiple queries
- **Headless browser** — powered by Playwright, fully automatable

## 🚀 Quick start

### Without Docker

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
# fill in your credentials
python main.py scrape
```

### With Docker

```bash
cp .env.example .env
# fill in your credentials
docker compose build
docker compose run --rm wttj-auto-apply scrape
```

## 📖 Usage

```
usage: main.py [-h] [-v] {scrape,apply,all}

WTTJ Job Bot — scrape companies and send spontaneous applications

positional arguments:
  {scrape,apply,all}
    scrape           Scrape companies matching your queries
    apply            Apply to companies scraped earlier
    all              Scrape then apply in one run

options:
  -h, --help         Show this help message and exit
  -v, --verbose      Enable debug logging
```

### 1. Configuration

Create a `.env` file based on `.env.example`:

```env
EMAIL=your.email@example.com
PASSWORD=your_password
QUERIES='["backend", "devops", "data"]'
REGION=paris                     # optional
BLACKLIST=google,meta            # optional, comma-separated
LETTER_FILE=motivation_letter.txt # optional, defaults to motivation_letter.txt
```

Create a `motivation_letter.txt` file with your cover letter text.

### 2. Scrape companies

```bash
python main.py scrape
```

This fetches all companies matching your queries, filters out blacklisted ones, and saves them to `enterprises.json`.

### 3. Apply automatically

```bash
python main.py apply
```

Logs into WTTJ and sends a spontaneous application to every company found.

### 4. Do both at once

```bash
python main.py all
```

## 🏗️ Architecture

```
main.py                  CLI entry point (argparse)
├── wttj_scraper.py      Fetches companies from WTTJ
├── wttj_applier.py      Sends spontaneous applications
└── wttj_utils.py        Shared types and helpers (Company dataclass, URL)
```

## 🐳 Docker

```bash
# Build
docker compose build

# Run scrape
docker compose run --rm wttj-auto-apply scrape

# Run apply
docker compose run --rm wttj-auto-apply apply

# Run all
docker compose run --rm wttj-auto-apply -v all
```

> **Note:** Playwright needs a display to run the browser. On Linux, `docker-compose.yml` forwards your `$DISPLAY`. On macOS, you may need to run without Docker or use XQuartz.

## 📄 License

MIT
