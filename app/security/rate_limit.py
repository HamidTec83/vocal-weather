"""
rate_limit.py

Configuration du rate limiting.

Objectif :
- limiter le nombre de requêtes par IP
- protéger l'API contre les abus simples
"""

from slowapi import Limiter
from slowapi.util import get_remote_address


# Limiter global utilisé dans les routers FastAPI
limiter = Limiter(
    key_func=get_remote_address
)