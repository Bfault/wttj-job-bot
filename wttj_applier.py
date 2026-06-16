import json
import logging
import os

from playwright.sync_api import Page, sync_playwright

from wttj_utils import Company, URL, get_env

log = logging.getLogger(__name__)


def _apply_to_company(page: Page, company: Company, letter: str) -> bool:
    url = f"{URL}/companies/{company.link}/jobs"
    page.goto(url)
    page.wait_for_timeout(2000)

    selectors = [
        '//div[.//span[text()="Candidature spontanée"]]//button[@data-testid="company_jobs-button-apply"]',
        '//div[.//span[text()="Spontaneous application"]]//button[@data-testid="company_jobs-button-apply"]',
    ]

    button = None
    for sel in selectors:
        btn = page.locator(sel)
        if btn.count() > 0:
            button = btn
            break

    if button is None:
        log.info("  No spontaneous application button for %s", company.name)
        return False

    button.click()
    page.wait_for_timeout(2000)

    textfield = page.locator('[data-testid="apply-form-field-cover_letter"]')
    if textfield.count() > 0:
        textfield.fill(letter)

    for sel in [
        '[data-testid="apply-form-terms"]',
        '[data-testid="apply-form-consent"]',
    ]:
        try:
            page.click(sel)
            page.wait_for_timeout(500)
        except Exception:
            pass

    page.click('[data-testid="apply-form-submit"]')
    page.wait_for_timeout(2000)
    log.info("  Applied to %s", company.name)
    return True


def apply(companies_file: str = "enterprises.json") -> None:
    from dotenv import load_dotenv

    load_dotenv()

    with open(companies_file) as f:
        data = json.load(f)

    companies = [Company(name=item["name"], link=item["link"]) for item in data]
    log.info("Loaded %d companies from %s", len(companies), companies_file)

    letter_file = os.environ.get("LETTER_FILE", "motivation_letter.txt")
    try:
        with open(letter_file) as f:
            letter = f.read().strip()
    except FileNotFoundError:
        log.error("Motivation letter not found: %s", letter_file)
        return

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

        success = 0
        for i, company in enumerate(companies, 1):
            log.info("[%d/%d] Processing %s", i, len(companies), company.name)
            if _apply_to_company(page, company, letter):
                success += 1

        log.info("Done. Applied to %d / %d companies", success, len(companies))
        browser.close()
