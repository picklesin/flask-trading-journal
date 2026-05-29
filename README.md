# Trading Journal — Flask Web Application

**Live Demo:** [trading-journal-btms.onrender.com](https://flask-trading-journal-1.onrender.com)

## Overview

A full stack web application built with Flask that helps traders track, review, and analyze their trades in one place. The application includes secure authentication, trade logging, performance tracking, and an interactive dashboard to help users improve trading discipline and decision-making.

---

## Features

- User registration and authentication with email verification
- Secure password hashing with Flask-Bcrypt
- Login session management with Flask-Login
- Trade entry and trade history tracking
- Interactive dashboard with cumulative P&L, win rate, and avg win/loss charts
- Form validation with WTForms
- Password reset via email
- Database integration with SQLAlchemy
- Database migrations using Flask-Migrate
- Responsive Flask templates

---

## Tech Stack

### Backend
- Python / Flask
- SQLAlchemy
- Flask-Login
- Flask-WTF
- Flask-Bcrypt
- Flask-Migrate
- Flask-Mail

### Database
- PostgreSQL (production)
- SQLite (local development)

### Frontend
- HTML / CSS
- Jinja2 Templates
- Chart.js

### Additional Libraries
- NumPy
- itsdangerous


## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/picklesin/trading-journal.git
cd trading-journal
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

**Windows**
```bash
venv\Scripts\activate
```

**macOS/Linux**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file in the root directory:

```env
SQLALCHEMY_DATABASE_URI=sqlite:///site.db
SECRET_KEY=your-secret-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_DEFAULT_SENDER=your@gmail.com
```

> **Note:** For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) rather than your regular password.

### 5. Run Database Migrations

```bash
flask db upgrade
```

### 6. Start the Application

```bash
flask run
```

---

## Deployment

Deployed on [Render](https://render.com) with a PostgreSQL database. Environment variables are configured via Render's dashboard. Migrations run automatically on each deploy via the build command.

---

## Security Features

- Password hashing with Flask-Bcrypt
- Session authentication with Flask-Login
- CSRF protection with Flask-WTF
- Secure token generation with itsdangerous

---

## Future Improvements

- Transactional email via Resend API
- CSV import/export
- Risk management metrics (R-multiple, max drawdown)
- Advanced filtering and search
- Mobile optimization
- Broker API integration
