from flask import Flask, render_template, request, jsonify
from chatbot import index_website, search
import threading
import time

app = Flask(__name__)

app.config['SERVER_NAME'] = 'localhost:5000'

@app.route('/')
def home():
    return render_template('home.html', title='Home')

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/services')
def services():
    return render_template('services.html', title='Services')

@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')

@app.route('/team')
def team():
    return render_template('team.html', title='Team')

@app.route('/faq')
def faq():
    return render_template('faq.html', title='FAQ')

@app.route('/chat', methods=['POST'])
def chat():
    query = request.json.get('query')
    results = search(query, None)
    return jsonify({'results': results})

def start_crawling(base_url):
    time.sleep(2)
    with app.app_context():
        index_website(base_url)

if __name__ == '__main__':
    base_url = "http://localhost:5000"
    crawl_thread = threading.Thread(target=start_crawling, args=(base_url,))
    crawl_thread.start()
    app.run(debug=True, port=5000)