# book_fetcher.py
"""
Module to fetch and structure book data from Google Books API, including price information.
Caches previous query results in memory.
"""
import requests
from config import GOOGLE_BOOKS_API_URL, DEFAULT_QUERY, DEFAULT_MAX_RESULTS
from requests.exceptions import HTTPError

# Simple in-memory cache: stores last query parameters and results
_cache = {
    "query": None,
    "results": []
}


def fetch_books(query: str = None, max_results: int = None):
    """
    Fetches books from Google Books API, includes price data if available.
    Applies in-memory caching for repeated queries.

    Args:
        query (str): Search term for books.
        max_results (int): Maximum number of results to fetch.

    Returns:
        List[dict]: List of book data dictionaries with title, description,
                    authors, price, source, and link.
    """
    global _cache
    q = query or DEFAULT_QUERY
    m = max_results or DEFAULT_MAX_RESULTS

    # Return cached results if same parameters
    if _cache["query"] == (q, m):
        return _cache["results"]

    params = {"q": q, "maxResults": m}
    try:
        resp = requests.get(GOOGLE_BOOKS_API_URL, params=params)
        resp.raise_for_status()
        items = resp.json().get("items", [])
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Log HTTP errors
        items = []
    except Exception as err:
        print(f"Other error occurred: {err}")  # Log other errors
        items = []

    books = []
    for item in items:
        info = item.get("volumeInfo", {})
        sale = item.get("saleInfo", {})
        list_price = sale.get("listPrice", {})
        # Numeric price for filtering; None if not available
        price_amount = list_price.get("amount")
        currency = list_price.get("currencyCode")
        books.append({
            "title": info.get("title", "N/A"),
            "description": (info.get("description") or "No description available")[:200],
            "authors": info.get("authors", ["Unknown"]),
            "price": price_amount,
            "currency": currency,
            "price_display": f"{price_amount} {currency}" if price_amount else "N/A",
            "source": "Google Books",
            "link": info.get("infoLink", "#")
        })

    # Update cache
    _cache = {
        "query": (q, m),
        "results": books
    }
    return books
