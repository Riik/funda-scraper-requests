#!/usr/bin/env python
# coding: utf-8

import sqlite3
from sqlite3 import OperationalError

from funda_scraper import FundaScraper

TABLE_NAME = "houses"

if __name__ == "__main__":
    ctx = sqlite3.connect("db/listings.db")

    try:
        known_urls = set([row[0] for row in ctx.execute(f"SELECT url FROM {TABLE_NAME}").fetchall()])
    except OperationalError:
        known_urls = set()

    scraper = FundaScraper(
        area="delft",
        want_to="buy",
        find_past=False,
        page_start=1,
        n_pages=10,
        max_price=500000,
        extra_args={"floor_area": '"75-"', "object_type": '["house"]'},
        known_urls=known_urls,
    )

    df = scraper.run(raw_data=True, save=False)

    if not df.empty:
        df["identifier"] = df["url"].str.split("/").str[-2]
        df["notification_sent"] = 0
        df.set_index("identifier")

        df.to_sql(name=TABLE_NAME, con=ctx, index=False, if_exists="append")
        ctx.commit()

    ctx.close()
