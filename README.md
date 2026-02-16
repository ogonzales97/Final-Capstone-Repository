# News Portal Capstone Project

A full-stack News Management System built with **Django**, **MariaDB**, and **Django REST Framework**.

## Features
* **Dual User Roles:** Journalists can submit stories; Editors can approve and publish them.
* **REST API:** Full API integration for article management.
* **Dynamic Frontend:** Built with JavaScript Fetch to provide a smooth user experience.
* **Database:** Robust data storage using MariaDB.

## Setup
1. Clone the repo.
2. Create a virtual environment: `python -m venv venv`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Configure your `.env` for MariaDB.
5. Run migrations: `python manage.py migrate`.
6. Start the server: `python manage.py runserver`.

## Key Technical Implementation
Role-Based Access Control (RBAC): Custom user model distinguishing between Readers, Journalists and Editors.

Persistent Data: Migration from SQLite to MariaDB for production-grade data management.

Asynchronus Operations: Used JavaScript fetch API for dynamic article updates without page reloads.

API Architecture: Implemented Django REST Framework for structured data handling.

## Future Planned Improvements
Image upload support.
Email notifications for approved stories.