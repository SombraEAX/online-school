# Online School Engine

A simple online school engine with courses, landing pages, and a Telegram chatbot.

## Features

- Adding content through the admin panel
- Customizable landing page appearance
- Telegram chatbot with lessons
- WYSIWYG article editor

## Quick Start (Local)

```bash
pip install -r requirements.txt
python seed.py          # seed database with demo data
python app.py           # start web app on :5000
python bot.py           # start Telegram bot (optional)
```

Default admin: `admin / admin123`

## Seed Data

Run `python seed.py` to populate the database with demo courses, lessons, landing pages, and articles. Safe to run multiple times — only seeds if the database is empty.

Seed images (course covers, landing backgrounds, author portraits) are stored in `static/seed/` and copied to `static/uploads/` during seeding. User-uploaded files also go to `static/uploads/` but use timestamped filenames, so there are no conflicts.

## Deployment (Render.com)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Connect your GitHub repository
2. Render will use `render.yaml` — it creates a web service, a bot worker, and a PostgreSQL database automatically
3. Set `BOT_TOKEN` manually in the Render dashboard (Environment → Secret Files)
4. Deploy — the `preDeployCommand: python seed.py` seeds the database

## Docker

```bash
docker build -t online-school .
docker run -d -p 5000:5000 -e FLASK_DEBUG=false --env-file .env --name online-school online-school
```

## Project Structure

```
├── app.py                 # Flask application
├── seed.py                # Database seeder
├── bot.py                 # Telegram bot
├── requirements.txt
├── render.yaml            # Render deployment config
├── Dockerfile
├── entrypoint.sh
├── static/
│   ├── css/style.css
│   ├── images/            # Static images (placeholder, etc.)
│   ├── seed/              # Seed data images (version-controlled)
│   └── uploads/           # User uploads (gitignored, persistent disk on Render)
└── templates/
    ├── base.html
    ├── landing.html
    ├── home_landing.html
    ├── courses.html
    ├── course_detail.html
    ├── lesson_detail.html
    ├── dashboard.html
    ├── admin*.html
    ├── edit_*.html
    ├── create_*.html
    └── macros.html
```

## Technologies

- **Backend:** Flask, SQLAlchemy (SQLite / PostgreSQL)
- **Frontend:** Bootstrap 5, Font Awesome
- **Bot:** python-telegram-bot
- **Auth:** Werkzeug password hashing
