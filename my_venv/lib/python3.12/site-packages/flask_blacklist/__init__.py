"""Public interface for importing Blacklist."""

from .base import Blacklist
from .utilities import is_blacklisted

__all__ = ["Blacklist", is_blacklisted]
