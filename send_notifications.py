#!/usr/bin/env python
# coding: utf-8

import sqlite3
import telegram
import json

TABLE_NAME = "houses"

if __name__ == "__main__":
    ctx = sqlite3.connect("db/listings.db")

    new_entries = ctx.execute(
        f"SELECT identifier, address, zip_code, price, living_area, num_of_rooms, url, year, energy_label, last_ask_price_m2 FROM {TABLE_NAME} WHERE notification_sent=0"
    ).fetchall()

    with open("telegram_config.json", "r") as f:
        config = json.load(f)

    token = config["api_key"]
    privateId = config["private_id"]
    groupId = config["group_id"]

    bot = telegram.Bot(token)

    for entry in new_entries:
        print(entry)

        (
            identifier,
            streetName,
            postalCode,
            listPrice,
            livingArea,
            numberOfRooms,
            listingLink,
            year,
            energy_label,
            ask_price_m2,
            *_,
        ) = entry
        postalCode = postalCode.split("        ")[-1]
        message = f"""<a href="{listingLink}">{streetName}, {postalCode}</a>: {listPrice}
    • Woon oppervlakte: {livingArea}
    • Kamers: {numberOfRooms} 
    • Bouwjaar: {year}
    • Prijs / m2: {ask_price_m2}
                   """

        print(message)

        print("Sending message")
        bot.send_message(text=message, chat_id=groupId, parse_mode=telegram.constants.PARSEMODE_HTML)
        print("Message sent")

        ctx.execute(f"UPDATE {TABLE_NAME} SET notification_sent=1 WHERE identifier='{identifier}'")
        ctx.commit()

    ctx.close()
