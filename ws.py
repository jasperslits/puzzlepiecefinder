"""Entry point for the PieceFinder server application."""
import asyncio

import piecefinder.server.websocket as ws

if __name__ == "__main__":
    asyncio.run(ws.main())
