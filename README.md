# 📰 Flask News Blog

A simple web application built using Flask that allows users to upload CSV files containing news articles and display them in a structured format categorized by state and district. The application stores the data in an SQLite database and provides an interactive interface to view the articles.

## 🚀 Features
- 📂 Upload CSV files containing news data
- 🗄️ Store data in an SQLite database
- 📰 Display news articles categorized by state and district
- 🔍 View detailed articles
- 🌐 Hosted on Heroku

## 🏗️ Installation

### 🔧 Prerequisites
Ensure you have the following installed on your system:
- Python 3.x 🐍
- pip (Python package manager) 📦
- Flask (Web framework) 🌍
- SQLite (Database) 🗃️

### 📥 Clone the Repository
```bash
git clone https://github.com/your-repo/flask-news-blog.git
cd flask-news-blog
```

### 📌 Install Dependencies
```bash
pip install -r requirements.txt
```

## 🏃 Running the Application Locally

### 🌱 Initialize the Database
```bash
python app.py
```
This will create `data.db` if it does not exist and set up the required tables.

### ▶️ Start the Flask Server
```bash
python app.py
```
The application will be accessible at:
```
http://127.0.0.1:5000/
```

## ☁️ Deploying to Heroku

### 📦 Install the Heroku CLI
If you haven't installed the Heroku CLI, download and install it from:
[Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

### 🔑 Login to Heroku
```bash
heroku login
```

### 🌍 Create a New Heroku App
```bash
heroku create your-app-name
```

### 🔄 Add Git Remote
```bash
git remote add heroku https://git.heroku.com/your-app-name.git
```

### 🛠️ Set Environment Variables (if needed)
```bash
heroku config:set FLASK_APP=app.py
heroku config:set FLASK_ENV=production
```

### 🚀 Deploy to Heroku
```bash
git push heroku main
```

### 🏁 Open the Deployed App
```bash
heroku open
```

Your application should now be live at:
```
https://your-app-name.herokuapp.com/
```

## ⚠️ **Troubleshooting: Website Not Opening?**

If your website is not opening due to a firewall restriction or network issue, try the following:
1. **Check if the app is running** using Heroku logs:
   ```sh
   heroku logs --tail
   ```
2. **Use a VPN** (e.g., ProtonVPN, Windscribe, or Opera VPN) to bypass restrictions.
3. **Try a web proxy** like [https://hide.me/en/proxy](https://hide.me/en/proxy).
4. **Access using HTTPS instead of HTTP**.
5. **Change your DNS settings** to Google DNS (8.8.8.8, 8.8.4.4) or Cloudflare DNS (1.1.1.1, 1.0.0.1).
6. **Try opening from another network or mobile data**.
   
## 📜 File Structure
```
flask-news-blog/
│── templates/        # HTML templates
│   ├── index.html
│   ├── blog.html
│   ├── news_list.html
│   ├── news_detail.html
│── static/           # CSS, JS, and other assets
│── app.py            # Flask application
│── requirements.txt  # Dependencies
│── data.db           # SQLite Database (Generated at runtime)
│── README.md         # Documentation
```

## 🛠️ Technologies Used
- Flask 🌍
- SQLite 🗃️
- HTML & CSS 🎨
- Bootstrap 🎭
- Heroku ☁️

## 🌟 Live Demo
Check out the live version of the app here:
🔗 [Flask News Blog](https://aqueous-springs-81139-b05cb2b0364d.herokuapp.com/blog)

---

📬 **Feel free to contribute, open issues, or fork this project!** 🛠️

