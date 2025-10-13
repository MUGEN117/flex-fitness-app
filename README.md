# Flex Fitness App

**Flex Fitness App** is a web application built with **Flask** that allows trainers and members to manage fitness routines, track meals, and log workouts. It supports user authentication, role-based dashboards, and a simple database for tracking users and food logs.

---

## **Features**

- User registration and login for **Trainers** and **Members**
- Role-based dashboards
  - Trainer Dashboard
  - Member Dashboard
- Secure password hashing with Werkzeug
- Food logging with calories, protein, carbs, and fat
- SQLite database using SQLAlchemy ORM
- Database migrations with Flask-Migrate / Alembic
- Responsive frontend using Bootstrap 5

---

## **Tech Stack**

- **Backend:** Python, Flask  
- **Database:** SQLite (via SQLAlchemy)  
- **Migrations:** Flask-Migrate / Alembic  
- **Frontend:** HTML, Bootstrap 5  
- **Security:** Werkzeug for password hashing  

---

## **Installation**

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/flex-fitness-app.git
cd flex-fitness-app
```

2. **Create and activate a virtual environment**

Windows:
```bash
python -m venv venv
.\venv\Scripts\Activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```
4. **Set environmental variables (optional)**
```bash
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///app/db.sqlite3
```
5. **Initialize the databse**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```
6. **Run the app**
```bash
python run.py
```

