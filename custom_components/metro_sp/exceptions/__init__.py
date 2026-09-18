"""Classes de exceção do cliente da API do metro_sp."""

from __future__ import annotations

from .api_client_communication_error import MetroSPApiClientCommunicationError
from .api_client_error import MetroSPApiClientError

__all__ = [
    "MetroSPApiClientCommunicationError",
    "MetroSPApiClientError",
]
