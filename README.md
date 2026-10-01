# ghst-bnet

An async Python client for the [Battle.net web APIs](https://community.developer.battle.net/documentation/world-of-warcraft).

Written by a real human.

## Usage

Usage is pretty simple, so I'll just give you a short code snippet.

This snippet requires a `.env` file in the working directory containing your `BNET_API_CLIENT_ID` and `BNET_API_CLIENT_SECRET`, but you could also just pass them directly, if you were feeling bold.
```py
import os
import asyncio

from dotenv import load_dotenv

from bnet.console import setup_logging
from bnet.api import AsyncBattleNetAPI

load_dotenv()

async def amain():
    setup_logging()

    client_id = os.getenv("BNET_API_CLIENT_ID")
    client_secret = os.getenv("BNET_API_CLIENT_SECRET")

    client = AsyncBattleNetAPI(client_id, client_secret)
    realm = await client.realms.get("moon-guard")
    if realm:
        print(realm.category)
        print(realm.timezone)

    kakapo = await client.items.get(163800)
    if kakapo:
        print(kakapo.sell_price)


if __name__ == "__main__":
    asyncio.run(amain())
```

>[!NOTE]
>All of the game data resources/models need to be added manually, so I only added those that were most relevant to me. There's a lot of endpoints missing still - I'll get to them eventually.

Currently supports:
- Achievements
- Titles
- Items
- Mounts
- Quests
- Quest categories
- Quest areas
- Quest types
- Realms

## Notes

If you're reading this - made you look.