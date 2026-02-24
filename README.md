# News Portal Capstone Project

A full-stack News Management System built with **Django**, **MariaDB**, and **Django REST Framework**.

## Features
* **Dual User Roles:** Journalists can submit stories; Editors can approve and publish them.
* **REST API:** Full API integration for article management.
* **Dynamic Frontend:** Built with JavaScript Fetch to provide a smooth user experience.
* **Database:** Robust data storage using MariaDB.

## Setup and Integration
This application is designed for professional integration with MySQL/MariaDB. Follow these 
steps to set up the application in your local environment.

### 1. Clone the Repository
```bash
git clone <your-github-repo-url>
cd "News Application"
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
The project uses `python-dotenv` to manage database connections and email credentials securely.

**Create a `.env` file** in the root directory (where `manage.py` is located) by copying the example:
```bash
cp .env.example .env
```

**Edit `.env`** with your local credentials:
```
DB_NAME=news_portal_db
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

### 5. Database Setup
Create the database in MySQL/MariaDB:
```sql
CREATE DATABASE news_portal_db;
```

Run migrations to create the schema:
```bash
python manage.py migrate
```

### 6. Load Sample Data
Load the pre-configured test users, roles, and articles:
```bash
python manage.py loaddata data.json
```

### 7. Run the Application
Start the development server:
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

## How to Test the Application

**Test Accounts:** Use these pre-configured accounts to verify role-based features:

**Password for all test accounts:** `Spacedoutclick999`


| Role | Username | Feature to Test |
|------|----------|----------------|
| Independent Journalist | Journalist | Create a story with "No Publisher" (Independent option) to verify Auto-Publish Bypass |
| Org Journalist | Journalist2 | Create a story for a specific publisher; it will wait for Editor approval |
| Editor | Editor | Access the Editor Dashboard to approve content or add/delete Publishers |
| Reader | Reader | Verify that administrative tools and edit buttons are hidden |

**Note:** These are demonstration accounts. In production, change all passwords and remove test data.

## Security Notes
- Never commit your `.env` file to version control
- Use strong passwords in production
- Test accounts included are for demonstration purposes only
- Replace Gmail credentials with your own for email functionality

## Key Technical Implementation
- **Role-Based Access Control (RBAC):** Custom user model distinguishing between Readers, Journalists, and Editors.
- **Persistent Data:** Migration from SQLite to MariaDB for production-grade data management.
- **Asynchronous Operations:** Used JavaScript Fetch API for dynamic article updates without page reloads.
- **API Architecture:** Implemented Django REST Framework for structured data handling.
- **Email Notifications:** Real-time email alerts sent to subscribers when articles are approved.

## Future Planned Improvements
- Image upload support for articles
- Advanced search and filtering capabilities
- Comment system for readers
- Social media sharing integration