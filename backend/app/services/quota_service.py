import logging
from typing import Optional

logger = logging.getLogger(__name__)


class QuotaExhaustedError(Exception):
    """Raised when the SerpApi session search budget is exhausted by the circuit breaker."""
    pass


class QuotaBudgetManager:
    """Tracks and enforces SerpApi live search call limits per investigation session.
    
    Prevents runaway agent loops and quota depletion during development and production runs.
    Crucial invariant: Cache hits NEVER consume budget; only live network calls do.
    """

    def __init__(self, max_budget: int = 8):
        self._max_budget = max(0, max_budget)
        self._consumed = 0

    def can_consume(self, count: int = 1) -> bool:
        """Check if sufficient search budget remains."""
        return (self._max_budget - self._consumed) >= count

    def consume(self, count: int = 1) -> None:
        """Decrement the search budget, raising QuotaExhaustedError if insufficient."""
        if not self.can_consume(count):
            remaining = self.remaining_budget()
            logger.warning(
                "Quota circuit breaker triggered! Attempted to consume %d queries, but only %d remaining (max=%d).",
                count,
                remaining,
                self._max_budget,
            )
            raise QuotaExhaustedError(
                f"SerpApi query budget exhausted. Required: {count}, Remaining: {remaining}, Max: {self._max_budget}."
            )
        self._consumed += count
        logger.debug(
            "Consumed %d SerpApi query credit(s). %d remaining out of %d.",
            count,
            self.remaining_budget(),
            self._max_budget,
        )

    def remaining_budget(self) -> int:
        """Return the number of remaining allowed live queries."""
        return max(0, self._max_budget - self._consumed)

    def consumed_budget(self) -> int:
        """Return the total number of consumed live queries."""
        return self._consumed

    def reset(self, new_max_budget: Optional[int] = None) -> None:
        """Reset the budget counter, optionally updating the maximum allowance."""
        if new_max_budget is not None:
            self._max_budget = max(0, new_max_budget)
        self._consumed = 0
        logger.info("Reset SerpApi quota budget to %d.", self._max_budget)
