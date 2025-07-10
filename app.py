# app.py
"""
Main Flask application for Smart Data Display (Trending Books).

This app uses the Google Books API to fetch and display a list of trending books,
including price information and filtering by price range.

Frontend (index.html) is served from the templates directory.
"""
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from book_fetcher import fetch_books, _cache
import config

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for frontend requests

@app.route("/")
def home():
    """
    Serves the home page with the HTML interface.
    """
    return render_template("index.html")

@app.route("/api/books", methods=["GET"])
def get_books():
    """
    Return the default list of books based on DEFAULT_QUERY.

    Returns:
        JSON response containing a list of books.
    """
    books = fetch_books()
    return jsonify(books)

@app.route("/api/books/search", methods=["GET"])
def search_books():
    """
    Search for books using query string, optional max_results,
    and filter by price range.

    Query Parameters:
        q (str): Search term (defaults to DEFAULT_QUERY)
        max_results (int): Number of results (defaults to DEFAULT_MAX_RESULTS)
        min_price (float): Minimum price filter (inclusive)
        max_price (float): Maximum price filter (inclusive)

    Returns:
        JSON list of matched books.
    """
    # Basic search parameters
    q = request.args.get('q', config.DEFAULT_QUERY)
    try:
        m = int(request.args.get('max_results', config.DEFAULT_MAX_RESULTS))
    except ValueError:
        m = config.DEFAULT_MAX_RESULTS

    # Price filters
    try:
        min_p = float(request.args.get('min_price'))
    except (TypeError, ValueError):
        min_p = None
    try:
        max_p = float(request.args.get('max_price'))
    except (TypeError, ValueError):
        max_p = None

    # Fetch books
    books = fetch_books(query=q, max_results=m)

    # Apply price filtering
    def price_in_range(book):
        price = book.get('price')
        if price is None:
            return False  # skip books without price
        if min_p is not None and price < min_p:
            return False
        if max_p is not None and price > max_p:
            return False
        return True

    if min_p is not None or max_p is not None:
        books = [b for b in books if price_in_range(b)]

    return jsonify(books)

@app.route("/api/books/refresh", methods=["POST"])
def refresh_books():
    """
    Clear in-memory cache and force re-fetch of book data.

    Returns:
        JSON with status and refreshed book count.
    """
    _cache['query'] = None
    books = fetch_books()
    return jsonify({"status": "refreshed", "count": len(books)})

if __name__ == "__main__":
    app.run(debug=True)  # Run Flask development server with debug mode enabled
