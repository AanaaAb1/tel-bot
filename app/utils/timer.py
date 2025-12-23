import time
import asyncio

async def exam_timer(duration_sec, callback, *args):
    """Run a countdown timer asynchronously. Calls callback after time is up."""
    await asyncio.sleep(duration_sec)
    await callback(*args)