# 🚀 Backend Setup Guide — Assistrend Backend

This project uses **Django**, **Celery**, **Redis**, and **Django Channels** to handle real-time messaging and background task cleanup efficiently.

---

## 📆 1. Install All Required Packages


pip install -r requirements.txt


Make sure your `requirements.txt` includes:


Django>=3.2
celery>=5.2
redis
channels
channels_redis


---

## 🔧 2. Redis Installation (for Celery + Channels)

Install Redis if it's not already installed.

### 🩟 On Windows (via Docker):


docker run -d --name redis -p 6379:6379 redis


---

## ⚙️ 3. Django Setup

Run database migrations:


python manage.py migrate


Create a superuser:


python manage.py createsuperuser


---

## 🧐 4. Celery Configuration Structure

**Directory layout:**


ASSISTREND_Backend/
├── manage.py
├── message_service/
│   ├── __init__.py
│   ├── celery_app.py
│   ├── settings.py
│   └── ...
├── message/
│   ├── tasks.py
│   ├── models.py
│   └── ...


---

## 🛠️ 5. Run the Django Development Server


python manage.py runserver


---

## 🔄 6. Run Celery Worker

Start the background task worker:


celery -A message_service worker --loglevel=info


---

## ⏱️ 7. Run Celery Beat (Scheduler)

Start Celery Beat to run periodic tasks (e.g. message cleanup):


celery -A message_service beat --loglevel=info


> Make sure both `worker` and `beat` are running in separate terminal tabs.

---

## 📱 8. Run Redis (If Not Using Docker)

If you prefer running Redis directly:

* Linux/macOS:

  
  redis-server
  
* Windows (via Redis MSI or Redis for WSL2)

---


