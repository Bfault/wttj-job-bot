#!/usr/bin/env python3
"""Welcome to the Jungle — automated job search tool.

Scrapes companies and optionally sends spontaneous applications.
"""

import argparse
import logging


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="WTTJ Auto-Apply — scrape companies and send spontaneous applications",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("scrape", help="Scrape companies matching your queries")
    sub.add_parser("apply", help="Apply to companies scraped earlier")
    sub.add_parser("all", help="Scrape then apply in one run")

    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.command == "scrape":
        from wttj_scraper import scrape
        scrape(save=True)

    elif args.command == "apply":
        from wttj_applier import apply
        apply()

    elif args.command == "all":
        from wttj_scraper import scrape
        from wttj_applier import apply

        companies = scrape(save=True)
        if not companies:
            print("No companies found. Nothing to apply to.")
            return
        apply()


if __name__ == "__main__":
    main()
