# safe_async.py — Utility to run an async coroutine safely from sync code
# Handles the case where an event loop is already running (e.g., in Tk) by
# spinning a dedicated loop in a background thread and joining.

from __future__ import annotations
import asyncio
from threading import Thread

def run_async(coro):
    """
    Run the given coroutine and return its result.
    - If there's no running loop, use asyncio.run.
    - If there is a running loop, run the coroutine in a fresh loop on a worker thread.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if not loop or not loop.is_running():
        return asyncio.run(coro)

    # Running loop detected: execute on a separate loop/thread and join
    result = {"value": None, "error": None}

    def _runner():
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            result["value"] = new_loop.run_until_complete(coro)
        except Exception as e:
            result["error"] = e
        finally:
            try:
                new_loop.run_until_complete(new_loop.shutdown_asyncgens())
            except Exception:
                pass
            new_loop.close()

    t = Thread(target=_runner, daemon=True)
    t.start()
    t.join()

    if result["error"] is not None:
        raise result["error"]
    return result["value"]
