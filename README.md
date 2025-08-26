# Polling System - Django Application

This is a simple **Polling System** built with Django, where users can register, login, create polls, vote, and view results.

---

## Features

* User Registration & Login (with authentication)
* Create polls with multiple options
* Vote on polls (1 vote per user per poll)
* View poll results
* Bootstrap-based responsive UI

---
## 📂 Project Structure

```
poll_system/
├── authentication/          # Authentication & RBAC logic
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py            # Custom User model with roles
│   ├── forms.py             # form creation
│   ├── serializers.py       # Serializers for User & Auth
│   ├── urls.py              # App-specific routes
│   ├── views.py             # API Views
│
├── poll_system/                  # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py          # Django settings (ENV support)
│   ├── urls.py              # Root URL configuration
│   ├── wsgi.py
│
├── manage.py                # Django CLI entry point
├── requirements.txt         # Project dependencies
├── .env                     # Environment variables (local)
├── .env.sample              # Example env file
```


## Setup Instructions

### 1. Clone and Setup Environment

```bash
# Clone repo (if hosted in GitHub, otherwise create manually)
git clone https://github.com/athishulleri01/poll-system.git
cd poll_system

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install django
```



## Run the Project

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser   # create admin user
python manage.py runserver
```

Open in browser: [http://127.0.0.1:8000](http://127.0.0.1:8000)

✅ Now you can **Register, Login, Vote, and See Results!**
