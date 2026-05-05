"""Constants for metro_sp."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "metro_sp"
ATTRIBUTION = "Dados fornecidos pelo Metrô SP / CPTM"
API_BASE_URL = "https://apim-proximotrem-prd-brazilsouth-001.azure-api.net/api/v1"
STATIC_URL_PREFIX = "/metro_sp"
