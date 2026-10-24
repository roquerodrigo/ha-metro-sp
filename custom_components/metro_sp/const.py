"""Constantes do metro_sp."""

from __future__ import annotations

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "metro_sp"
ATTRIBUTION = "Dados fornecidos pelo Metrô SP / CPTM"
API_BASE_URL = "https://fde-proximotrem-prd-hhbqdtdzdyhtgxhr.a01.azurefd.net/api/v1"
STATIC_URL_PREFIX = "/metro_sp"
