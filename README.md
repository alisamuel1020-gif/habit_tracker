# Habit Tracker Dashboard

A full-stack web application designed to help users build, track, and analyze daily habits. Features real-time visual analytics, custom desktop notifications, data export functionality, and secure multi-user authentication.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3.0-003B57?style=flat&logo=sqlite&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-4.0-FF6384?style=flat&logo=chart.js&logoColor=white)

---

## Features

* **User Authentication**: Secure register/login system powered by `Flask-Login` and hashed passwords via `Flask-Bcrypt`.
* **Habit Management**: Full CRUD operations to create, complete, edit, and delete daily habits.
* **Push Notifications**: In-browser desktop alerts triggered at user-defined reminder times using the Web Push API.
* **Analytics Dashboard**: Dynamic bar charts powered by `Chart.js` tracking total completion counts for each habit.
* **Data Export**: One-click downloadable CSV reports of habit completion logs.
* **Production-Ready**: Configured with `gunicorn` and environment variables for seamless deployment on platforms like Render or Railway.

---

## Tech Stack

* **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt
* **Frontend**: HTML5, CSS3, JavaScript (Fetch API, Web Notifications API), Chart.js
* **Database**: SQLite (Development) / PostgreSQL (Production)
* **WSGI Server**: Gunicorn

---

## Local Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/habit_tracker.git](https://github.com/YOUR_USERNAME/habit_tracker.git)
   cd habit_tracker