from flask import Flask, render_template, request, jsonify
from scraper import scrape_website
from llm_processor import process_text

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    scraped_data = scrape_website(url)
    if not scraped_data:
        return jsonify({"error": "Failed to scrape data"}), 500

    summary = process_text(scraped_data)
    return jsonify({"scraped": scraped_data, "summary": summary})


if __name__ == '__main__':
    app.run(debug=True)
