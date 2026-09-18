"""Erro de comunicação levantado pelo cliente da API."""

from __future__ import annotations

from .api_client_error import MetroSPApiClientError


class MetroSPApiClientCommunicationError(MetroSPApiClientError):
    """Exceção que indica um erro de comunicação."""
