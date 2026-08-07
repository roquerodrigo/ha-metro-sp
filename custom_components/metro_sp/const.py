"""Constants for metro_sp."""

from __future__ import annotations

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "metro_sp"
ATTRIBUTION = "Data provided by Metrô SP / CPTM"
API_BASE_URL = "https://apim-proximotrem-prd-brazilsouth-001.azure-api.net/api/v1"
STATIC_URL_PREFIX = "/metro_sp"
