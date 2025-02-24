import csv
from flask import Flask, request, render_template, redirect
import sqlite3
import os

app = Flask(__name__)

# SQLite database setup
DATABASE = 'data.db'

def init_db():
    if not os.path.exists(DATABASE):
        print("Database file does not exist. Creating a new one...")
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='csv_data'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Creating 'csv_data' table...")
            cursor.execute('''
                CREATE TABLE csv_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    headline TEXT,
                    link TEXT,
                    state TEXT,
                    district TEXT,
                    article_text TEXT,
                    summary TEXT,
                    keywords TEXT,
                    topic TEXT,
                    seo_title TEXT,
                    meta_description TEXT
                )
            ''')
            conn.commit()
        else:
            print("Table 'csv_data' already exists.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    if file and file.filename.endswith('.csv'):
        # Read CSV file
        csv_data = file.read().decode('utf-8').splitlines()
        csv_reader = csv.DictReader(csv_data)

        # Store each row in the SQLite database
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            for row in csv_reader:
                cursor.execute('''
                    INSERT INTO csv_data (
                        headline, link, state, district, article_text, 
                        summary, keywords, topic, seo_title, meta_description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['headline'], row['link'], row['state'], row['district'], 
                    row['article_text'], row['summary'], row['keywords'], 
                    row['topic'], row['seo_title'], row['meta_description']
                ))
            conn.commit()

        return "File uploaded and data stored in database successfully!", 200
    else:
        return "Invalid file type. Please upload a CSV file.", 400

@app.route('/news')
def news_list():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, headline, summary, link FROM csv_data")
        news_items = cursor.fetchall()
    return render_template('news_list.html', news_items=news_items)

@app.route('/news/<int:news_id>')
def news_detail(news_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM csv_data WHERE id = ?", (news_id,))
        news_item = cursor.fetchone()
    if news_item:
        return render_template('news_detail.html', news_item=news_item)
    else:
        return "News article not found", 404

# New route for the blog
@app.route('/blog')
def blog():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        # Fetch all articles grouped by state and district
        cursor.execute("SELECT state, district, id, headline, link, article_text, summary, keywords, topic, seo_title, meta_description FROM csv_data ORDER BY state, district")
        articles = cursor.fetchall()
    
    # Organize articles into a nested dictionary: {state: {district: [articles]}}
    organized_articles = {}
    for article in articles:
        state = article[0]  # State
        district = article[1]  # District
        if state not in organized_articles:
            organized_articles[state] = {}
        if district not in organized_articles[state]:
            organized_articles[state][district] = []
        organized_articles[state][district].append(article)
    
    return render_template('blog.html', organized_articles=organized_articles)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
