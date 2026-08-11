"""Runtime - manages the execution environment for the DAIOPH kernel."""

import threading
import time
from typing import Any, Callable, Dict, Optional


class Runtime:
    """Manages the execution runtime and worker pool."""

    def __init__(self, max_workers: int = 4) -> None:
        """Initialize the runtime.

        Args:
            max_workers: Maximum number of concurrent workers.
        """
        self._max_workers = max_workers
        self._threads: Dict[str, threading.Thread] = {}
        self._running = False
        self._start_time: Optional[float] = None

    def start(self) -> None:
        """Start the runtime."""
        self._running = True
        self._start_time = time.time()
        print(f"[Runtime] Started with up to {self._max_workers} workers")

    def submit(self, name: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Submit a task to run on a background thread.

        Args:
            name: Task name.
            fn: Callable to run.
            *args: Positional args.
            **kwargs: Keyword args.
        """
        thread = threading.Thread(
            target=fn, args=args, kwargs=kwargs, name=f"runtime-{name}", daemon=True
        )
        self._threads[name] = thread
        thread.start()

    def stop(self) -> None:
        """Stop the runtime."""
        self._running = False
        for name, thread in self._threads.items():
            if thread.is_alive():
                print(f"[Runtime] Waiting for {name} to finish...")
                thread.join(timeout=5)
        print("[Runtime] Stopped")

    @property
    def uptime(self) -> float:
        """Get runtime uptime in seconds."""
        return (time.time() - self._start_time) if self._start_time else 0.0

    @property
    def is_running(self) -> bool:
        """Whether the runtime is running."""
        return self._running

    def active_threads(self) -> int:
        """Get the number of active threads.

        Returns:
            int: Active thread count.
        """
        return sum(1 for t in self._threads.values() if t.is_alive())