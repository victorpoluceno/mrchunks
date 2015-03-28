try:
    import asyncio
except ImportError:
    # Use Trollius on Python <= 3.2
    import trollius as asyncio
