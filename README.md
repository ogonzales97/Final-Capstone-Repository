# News Portal Capstone Project

A full-stack News Management System built with **Django**, **MariaDB**, and **Django REST Framework**.

## Features
* **Dual User Roles:** Journalists can submit stories; Editors can approve and publish them.
* **REST API:** Full API integration for article management.
* **Dynamic Frontend:** Built with JavaScript Fetch to provide a smooth user experience.
* **Database:** Robust data storage using MariaDB.

## Table of Contents
- [Setup with Virtual Environment](#setup-with-virtual-environment)
- [Setup with Docker](#setup-with-docker)
- [How to Test the Application](#how-to-test-the-application)
- [Key Technical Implementation](#key-technical-implementation)

---

## Setup with Virtual Environment

### 1. Clone the Repository
```bash
git clone <your-github-repo-url>
cd "News Application"
```

### 2. Create and Activate Virtual Environment
**On macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt, indicating the virtual environment is active.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

#### Generate a Secret Key
Generate a secure Django secret key using this command:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copy the output - you'll need it in the next step.

#### Create Your `.env` File
The project includes a `.env.example` file as a template. Create your own `.env` file:

**On macOS/Linux:**
```bash
cp .env.example .env
```

**On Windows:**
```bash
copy .env.example .env
```

#### Edit the `.env` File
Open the `.env` file and replace the placeholder values with your actual credentials:

```bash
# Database Configuration
DB_NAME=news_portal_db
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

# Django Secret Key (paste the key you generated above)
# FOR THE REVIEWER: The secret key is already shown in SECRETS_FOR_REVIEWER.txt. This is a temporary .txt file that
# will ne removed after resubmission is no longer required.

SECRET_KEY=your-generated-secret-key-here
DEBUG=True

# Email Configuration (Gmail)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

**Important Notes:**
- Replace `your_mysql_username` and `your_mysql_password` with your actual MySQL/MariaDB credentials
- Paste the secret key you generated in the previous step
- For Gmail, you need to generate an [App Password](https://support.google.com/accounts/answer/185833)
- **Never commit the `.env` file to version control** - it's already in `.gitignore`

### 5. Database Setup

#### Create the Database
First, create the database in MySQL/MariaDB. Log into MySQL:
```bash
mysql -u your_username -p
```

Then create the database:
```sql
CREATE DATABASE news_portal_db;
EXIT;
```

#### Run Migrations
Apply the database migrations to create all necessary tables:
```bash
python manage.py migrate
```

This command will create all the required database tables based on your Django models.

### 6. Create a Superuser
Create an admin account to access the Django admin interface:
```bash
python manage.py createsuperuser
```

Follow the prompts to set up your admin username, email, and password.

### 7. Run the Application
Start the development server:
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

**To access the admin panel:** `http://127.0.0.1:8000/admin`

---

## Setup with Docker

Docker simplifies the setup process by containerizing the application and its dependencies.

### Prerequisites
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Ensure Docker is running

### 1. Clone the Repository
```bash
git clone <your-github-repo-url>
cd "News Application"
```

### 2. Environment Configuration

#### Generate a Secret Key
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

#### Create Your `.env.docker` File for Docker
```bash
cp .env.docker.example .env.docker
```

Edit the `.env.docker` file with your configuration:
```bash
# Database Configuration (Docker uses these defaults from docker-compose.yml)
DB_NAME=news_portal_db
DB_USER=newsuser
DB_PASSWORD=newspassword
DB_HOST=db
DB_PORT=3306

# Django Secret Key (paste the key you generated above)
SECRET_KEY=your-generated-secret-key-here
DEBUG=True

# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

**Important:** The database credentials here should match those in `docker-compose.yml` (lines 6-9). The `DB_HOST` must be set to `db` (the service name).

**Note:** When using Docker, `DB_HOST` should be set to `db` (the service name in docker-compose.yml).

### 3. Build and Run with Docker Compose
```bash
docker-compose up --build
```

This command will:
- Build the Django application container
- Set up a MariaDB database container
- Link the containers together
- Start both services

### 4. Run Migrations (in a new terminal)
While the containers are running, open a new terminal and run:
```bash
docker-compose exec web python manage.py migrate
```

### 5. Create a Superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

### 6. Access the Application
Visit `http://127.0.0.1:8000` in your browser.

### Stopping Docker
To stop the containers:
```bash
docker-compose down
```

To stop and remove all data (including the database):
```bash
docker-compose down -v
```

---

## How to Test the Application

Once the application is running, you can create test accounts with different roles:

### Creating Test Users via Admin Panel

1. Log in to the admin panel at `http://127.0.0.1:8000/admin`
2. Click on "Users" → "Add User"
3. Create users with different roles:
   - **Reader:** Can view articles and subscribe to publishers/journalists
   - **Journalist:** Can create articles (pending editor approval if associated with a publisher)
   - **Editor:** Can approve articles, manage publishers, and access the editor dashboard

### Testing Key Features

| Role | Feature to Test | How to Test |
|------|----------------|-------------|
| **Independent Journalist** | Auto-Publish Bypass | Create an article with "No Publisher" - it should publish immediately without editor approval |
| **Organization Journalist** | Approval Workflow | Create an article for a specific publisher - it will wait in "Pending" status for editor approval |
| **Editor** | Content Approval | Access the Editor Dashboard to approve/reject pending articles and manage publishers |
| **Reader** | Subscription & Notifications | Subscribe to publishers/journalists and verify email notifications when articles are approved |

### Testing the REST API

The application includes a full REST API. You can test endpoints using tools like:
- **Browser:** Visit `http://127.0.0.1:8000/api/`
- **Postman or cURL:** Test POST, PUT, DELETE operations
- **Django REST Framework UI:** Interactive API documentation

---

## Security Notes
- **Never commit your `.env` file** - it contains sensitive credentials
- The `.env.example` file is safe to commit - it only contains placeholders
- Use strong, unique passwords for production environments
- For Gmail integration, use [App Passwords](https://support.google.com/accounts/answer/185833), not your regular password
- Change `DEBUG=False` in production
- Generate a new `SECRET_KEY` for production (don't reuse development keys)

---

## Key Technical Implementation
- **Role-Based Access Control (RBAC):** Custom user model with distinct roles (Reader, Journalist, Editor)
- **Environment Variables:** Secure credential management using `python-dotenv`
- **Persistent Data:** MariaDB/MySQL for production-grade data management
- **Asynchronous Operations:** JavaScript Fetch API for dynamic updates without page reloads
- **RESTful API:** Django REST Framework with serializers and viewsets
- **Email Notifications:** Automated subscriber notifications when articles are approved
- **Approval Workflow:** Editor approval system for publisher-affiliated content
- **Docker Support:** Containerized deployment for consistency across environments

---

## Project Structure
```
News Application/
├── news_api/              # Main Django app
│   ├── models.py         # User, Article, Publisher, Subscription models
│   ├── views.py          # API viewsets and authentication views
│   ├── serializers.py    # DRF serializers
│   ├── permissions.py    # Custom permission classes
│   └── forms.py          # User registration forms
├── news_portal/          # Django project settings
│   └── settings.py       # Project configuration
├── static/               # CSS, JavaScript
├── templates/            # HTML templates
├── .env.example          # Environment variable template
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
└── manage.py             # Django management script
```

---

## Troubleshooting

### Virtual Environment Issues
**Problem:** `venv` not activating
- **Solution:** Make sure you're in the project directory and using the correct activation command for your OS

### Database Connection Issues
**Problem:** "Can't connect to MySQL server"
- **Solution:** Verify MySQL/MariaDB is running and credentials in `.env` are correct
- Check that the database `news_portal_db` exists

### Docker Issues
**Problem:** Port already in use
- **Solution:** Stop any services using port 8000 or 3306, or modify ports in `docker-compose.yml`

**Problem:** Permission denied errors
- **Solution:** On Linux/Mac, try running Docker commands with `sudo`

### Email Not Sending
**Problem:** Email notifications not working
- **Solution:** Verify you're using a Gmail App Password, not your regular password
- Check that `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are set correctly in `.env`

---

## Future Planned Improvements
- Image upload support for articles
- Advanced search and filtering capabilities
- Comment system for readers
- Social media sharing integration
- User profile pages with activity history