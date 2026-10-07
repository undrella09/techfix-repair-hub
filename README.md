# TechFix Repair Hub

A simple full-stack **computer and cellphone repair shop management system** built with Flask, SQLite, SQLAlchemy, Bootstrap 5, and Werkzeug.

## Business Description

**TechFix Repair Hub** is a fictional but realistic repair shop that provides computer, laptop, cellphone, and small-device repair services.

The system is used by two types of users:

- **Admin** — manages customers and all repair jobs.
- **Customer** — creates repair requests and can view and manage their own Pending requests.

## Problem Being Solved

The repair shop can lose information when repair requests are managed manually. Customers may also need to call repeatedly just to ask for the repair status.

This system keeps repair records in one persistent database and gives customers a simple way to submit and monitor their own repair jobs.

## Core CRUD Entity

**RepairJob**

Each repair job stores:

- Customer
- Device type
- Brand
- Model
- Problem description
- Repair status
- Estimated cost
- Created date
- Updated date

## Features

### Landing Page
- Public homepage with business name and description
- Repair service list
- Local repair illustration
- Call-to-action buttons
- Login and Register buttons
- Contact information
- Mobile-friendly Bootstrap layout

### Users
- Registration
- Login
- Logout
- Password hashing with Werkzeug
- Admin and Customer roles
- Protected routes
- Server-side role and ownership checks

### CRUD
- Create Repair Job
- Read Repair Jobs
- Update Repair Jobs
- Delete Repair Jobs
- Server-side validation
- Delete confirmation
- SQLite persistence

## Technology Stack

- Python 3
- Flask
- Flask-SQLAlchemy
- SQLite
- SQLAlchemy
- Werkzeug
- HTML
- CSS
- JavaScript
- Bootstrap 5

## Project Structure

```text
techfix-repair-hub/
├── app.py
├── config.py
├── extensions.py
├── requirements.txt
├── README.md
├── seed.py
├── .gitignore
├── .env.example
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── repair_job.py
├── routes/
│   ├── __init__.py
│   ├── main.py
│   ├── auth.py
│   ├── admin.py
│   └── customer.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── 403.html
│   ├── 404.html
│   ├── 500.html
│   ├── partials/
│   │   └── repair_table.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── repair_jobs.html
│   │   ├── repair_form.html
│   │   ├── repair_detail.html
│   │   └── customers.html
│   └── customer/
│       ├── dashboard.html
│       ├── repair_jobs.html
│       ├── repair_form.html
│       └── repair_detail.html
└── static/
    ├── css/style.css
    ├── js/script.js
    └── images/repair-shop.svg
```

## Setup and Run

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd techfix-repair-hub
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Optional: create environment settings

Copy `.env.example` to `.env` and replace `SECRET_KEY` with a random development secret.

Do **not** commit the `.env` file.

### 5. Create the database and demo data

```bash
python seed.py
```

This creates the SQLite database automatically and adds development/demo accounts and sample repair jobs.

### 6. Start the app

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Development / Demo Test Accounts

These credentials are for local demonstration only.

### Admin

```text
Email: admin@techfix.test
Password: Admin123!
Role: admin
```

### Customer

```text
Email: customer@techfix.test
Password: Customer123!
Role: customer
```

## How to Test

### Landing Page
1. Open the homepage without logging in.
2. Confirm the business name, description, services, image, contact information, and CTA buttons are visible.
3. Test the layout at a narrow mobile width.

### Registration
1. Register a new customer.
2. Try registering the same email again.
3. Try a password shorter than 8 characters.
4. Try mismatched password confirmation.
5. Submit required fields empty.

### Login / Logout
1. Log in with the admin account and confirm it opens the admin dashboard.
2. Log in with the customer account and confirm it opens the customer dashboard.
3. Test an incorrect password and confirm the site only shows `Invalid email or password.`
4. Logout and try opening a protected dashboard URL directly.

### Admin CRUD
1. Login as admin.
2. Create a repair job.
3. Read/view the repair job in the table.
4. Edit the repair job.
5. Change its status.
6. Delete the repair job.
7. Confirm that a browser delete confirmation appears.

### Customer CRUD / Ownership
1. Login as customer.
2. Create a Pending repair request.
3. View the request.
4. Edit the Pending request.
5. Delete the Pending request.
6. Verify a customer sees only their own repair records.
7. Change a request out of Pending and verify the customer can no longer edit/delete it.

### Persistence
1. Create a repair job.
2. Stop the Flask application.
3. Start it again.
4. Confirm the repair job is still in the database.

## Security Notes

- Passwords are stored using Werkzeug password hashes, never plain text.
- Admin/customer permissions are checked on the server.
- Customer repair records are protected by ownership checks.
- The customer role cannot be changed from the customer UI.
- SQLAlchemy is used for database access.
- `.env` is ignored by Git.
- The development fallback secret in `config.py` should be replaced in deployment.

## AI Tools Used

ChatGPT was used as a coding assistant to help with:

- Project planning
- Generating initial code
- Debugging and reviewing
- Explaining code
- Improving documentation
- Checking the assignment requirements

The student is responsible for reviewing, testing, modifying, and understanding the final code.

## Requirements Checklist

- [x] Public landing page
- [x] Business information
- [x] Services
- [x] Image
- [x] Call to action
- [x] Responsive design
- [x] User registration
- [x] User login
- [x] User logout
- [x] Hashed passwords
- [x] Admin role
- [x] Customer role
- [x] Protected pages
- [x] Create repair job
- [x] Read repair jobs
- [x] Update repair jobs
- [x] Delete repair jobs
- [x] Input validation
- [x] Delete confirmation
- [x] Persistent database
- [x] Test accounts
- [x] AI disclosure

## Requirements Audit

| Requirement | Implemented | Where |
|---|---|---|
| Landing Page | YES | `/` |
| Registration | YES | `/register` |
| Login | YES | `/login` |
| Logout | YES | `/logout` |
| Password Hashing | YES | `routes/auth.py` |
| Admin Role | YES | `routes/admin.py` |
| Customer Role | YES | `routes/customer.py` |
| Create | YES | Admin + Customer repair forms |
| Read | YES | Admin/Customer repair detail pages |
| Update | YES | Admin + Pending Customer requests |
| Delete | YES | Admin + Pending Customer requests |
| Validation | YES | `routes/auth.py`, `routes/admin.py`, `routes/customer.py` |
| Persistent Database | YES | SQLite + SQLAlchemy |
| Delete Confirmation | YES | Repair job delete forms |
| Responsive | YES | Bootstrap 5 + `style.css` |
| README | YES | `README.md` |
| AI Disclosure | YES | `README.md` |

## Important Note

This is a school-project system, not a production repair-shop application. Before production deployment, add stronger protections such as CSRF protection, a production secret, HTTPS, and a production database.
