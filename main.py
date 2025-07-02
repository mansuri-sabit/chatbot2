# app.py

import os
import logging
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from scraper import scrape_site

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY missing in .env file")

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Automatically crawl base website
BASE_URL = "https://troikaai.com/classes/"
print("🔍 Scraping website ali.bot...")
website_data = scrape_site(BASE_URL)
print("✅ Website scraped.")

# Flask setup
app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "No message provided."})

        prompt = f"""
You are a helpful assistant for Troika Tech.
Use the website content below to answer the user's question.

Website Content:
{website_data}

Question:
{user_message}
"""

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            logging.error("❌ Gemini API Error: %s", response.text)
            return jsonify({"reply": "Gemini API Error"}), 500

        reply_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"reply": reply_text})

    except Exception as e:
        logging.exception("❌ Chat Error:")
        return jsonify({"reply": "Oops! Something went wrong."}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8080)
