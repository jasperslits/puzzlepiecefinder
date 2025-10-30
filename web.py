"""Entry point for the PieceFinder server application."""
import asyncio

from piecefinder.server import web

if __name__ == "__main__":
    asyncio.run(web.main())
