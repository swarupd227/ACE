"""PMS/EHR connector seam (E1). Practice Admin today; Epic and others slot in behind the
same `PMSConnector` interface."""
from . import handoff  # noqa: F401
from .practice_admin import get_connector  # noqa: F401
