import json
import logging
import os

from bs4 import BeautifulSoup
from playwright.sync_api import Page

from wttj_utils import Company, URL

log = logging.getLogger(__name__)


def _select_region(page: Page) -> None:
    region = os.environ.get("REGION")
    if not region:
        return
    page.fill('[data-testid="companies-search-search-field-location"]', region.lower())
    page.wait_for_timeout(1500)
    page.click('[data-testid="place-item-0"]')
    page.wait_for_timeout(1500)


def _fetch_page(page: Page, query: str, page_num: int) -> list[Company]:
    if page_num > 1:
        page.locator(
            f'//nav[@aria-label="Pagination"]//a[normalize-space(text())="{page_num}"]'
        ).click()
        page.wait_for_timeout(2000)

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")
    companies: list[Company] = []
    cards = soup.select('[data-testid="companies-search-search-results"] li')

    for card in cards:
        article = card.find("article", {"data-testid": "company-card"})
        if not article:
            continue
        img = article.find("img")
        link = article.find("a")
        if not img or not link:
            continue
        name = img.get("alt", "").strip()
        href = link.get("href", "").strip().split("/")[-1]
        if not name or not href:
            continue
        companies.append(Company(name=name, link=href))

    return companies


def get_companies(
    page: Page,
    query: str,
    blacklist: set[str] | None = None,
) -> list[Company]:
    blacklist = blacklist or set()
    log.info("Fetching companies for query: %s", query)

    url = f"{URL}/companies?query={query}&page=1"
    page.goto(url)
    page.wait_for_timeout(2000)

    _select_region(page)

    try:
        page.get_by_label("Candidatures spontanées acceptées").click()
        page.wait_for_timeout(2000)
    except Exception:
        log.warning("Could not find spontaneous applications filter")

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")
    pagination = soup.select('[data-testid="companies-search-pagination"] li')
    last_page = 1
    if len(pagination) >= 2:
        last_page = int(pagination[-2].get_text(strip=True))

    log.info("Found %d pages for query '%s'", last_page, query)
    all_companies: list[Company] = []

    for n in range(1, last_page + 1):
        companies = _fetch_page(page, query, n)
        for c in companies:
            if c.name.lower() in blacklist:
                continue
            all_companies.append(c)

    return all_companies


def scrape(save: bool = False) -> list[Company]:
    from dotenv import load_dotenv
    from playwright.sync_api import sync_playwright

    from wttj_utils import get_env

    load_dotenv()

    queries = json.loads(get_env("QUERIES"))
    blacklist_raw = os.environ.get("BLACKLIST", "")
    blacklist = {line.strip().lower() for line in blacklist_raw.split(",") if line.strip()}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL)
        page.wait_for_timeout(2000)

        page.click('[data-testid="not-logged-visible-login-button"]')
        page.fill('[data-testid="login-field-email"]', get_env("EMAIL"))
        page.fill('[data-testid="login-field-password"]', get_env("PASSWORD"))
        page.click('[data-testid="login-button-submit"]')
        page.wait_for_timeout(3000)

        all_companies: list[Company] = []
        for query in queries:
            all_companies.extend(get_companies(page, query, blacklist))

        seen: dict[str, Company] = {}
        for c in all_companies:
            seen[c.name.lower()] = c
        unique = list(seen.values())

        log.info("Found %d unique companies", len(unique))
        for c in unique:
            print(f"  {c.name}: {URL}/companies/{c.link}")

        if save:
            with open("enterprises.json", "w") as f:
                json.dump([{"name": c.name, "link": c.link} for c in unique], f, indent=4)
            log.info("Saved results to enterprises.json")

        page.wait_for_timeout(2000)
        browser.close()

    return unique
