# Finance Data Processing and Access Control Backend

A robust RESTful API backend built with Django, designed to manage financial records, process aggregated dashboard analytics, and enforce strict Role-Based Access Control (RBAC) using JSON Web Tokens (JWT).

This project was built to demonstrate clean API architecture, database optimization, and secure data handling.

## Key Features

* **Role-Based Access Control (RBAC):** Three distinct user tiers (Admin, Analyst, Viewer) managed via Django Groups.
* **JWT Authentication:** Stateless, secure authentication via custom decorator wrappers.
* **Dashboard Analytics:** Highly optimized data aggregation (Period-over-Period trends, Category velocity) using Django ORM `.annotate()` and `.aggregate()` to push math to the database layer.
* **Dynamic Filtering & Pagination:** Robust query parameter filtering (by date, type, category) and dynamic pagination for scalable data fetching.
* **Full CRUD Operations:** Complete management of financial records and users for Admin roles.

## Tech Stack

* **Language:** Python 3.x
* **Framework:** Django (RESTful API architecture without DRF)
* **Authentication:** PyJWT (JSON Web Tokens)
* **Database:** SQLite (Default for easy local setup, easily swappable to PostgreSQL)

## Design Decisions & Assumptions

* **Stateless API:** I chose to completely bypass Django's default session-cookie authentication in favor of JWTs. A custom `@jwt_required` decorator intercepts the token, decodes it, and attaches the user to the request object.
* **RBAC Implementation:** I mapped roles directly to Django's built-in `auth_group` table.
    * **Viewers:** Can access high-level dashboard summaries but are blocked from viewing granular transaction lists.
    * **Analysts:** Can view dashboard summaries and all granular transaction lists, plus utilize dynamic filtering.
    * **Admins:** Full read/write access. Can create, edit, and delete both users and financial records.
* **Database Optimization:** Dashboard summaries do not pull all records into Python memory. Instead, `.values()` and `.annotate()` are used to perform summation and grouping at the SQL level for maximum performance.

## Local Setup Instructions

**1. Clone the repository and navigate into the directory**
```bash
git clone https://github.com/Muskan-Tarafder/Finance_Backend_Assignment.git
cd finance_backend
```

**2. Create and activate a virtual environment.**

```bash
# Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```
**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Apply database migrations**

```bash
python manage.py migrate
```

**5. Create the initial User Roles (Groups)**

Note: You must create the "Admin", "Analyst", and "Viewers" groups in your database for the RBAC logic to work properly.

```bash
python manage.py shell
```
```bash Python
from django.contrib.auth.models import Group
Group.objects.create(name='Admin')
Group.objects.create(name='Analyst')
Group.objects.create(name='Viewers')
exit()
```

**6. Create an Admin Superuser**

```bash
python manage.py createsuperuser
```

**7. Run the development server**

```bash
python manage.py runserver
```

**API Endpoints Reference**

Authentication
```bash
POST /api_login/ - Returns JWT and user role.
```
Dashboard & Analytics (Analysts & Admins)
```bash

GET /dashboard/ - High-level aggregates, net balance, and monthly/weekly trends.

GET /dashboard/filter_records/ - Paginated list of records. Supports query params: ?type=, ?category=, ?start_date=, ?end_date=, ?page=.

GET /dashboard/expense_list/ - Paginated list of all expenses.

GET /dashboard/income_list/ - Paginated list of all income.
```
Admin Management (Admins Only)
```bash
POST /adminpage/create_user/ - Creates a new user and assigns a role.

POST /adminpage/add_finance/ - Create a new financial record.

PATCH /adminpage/edit_finance/<int:id>/ - Partially update a record.

DELETE /adminpage/delete_finance/<int:id>/ - Delete a record.
```

**Testing the API**
To test this API, you can use Postman.

Hit the api_login endpoint with your username and password.

Copy the returned token.

For all subsequent requests, include the token in the Headers:
```bash
Authorization: Bearer <your_token>
```

## Assumptions & Tradeoffs

**Assumptions Made:**
* **Role Permissions:** I assumed that "Viewers" are allowed to see the high-level aggregated dashboard data (trends, totals) but are explicitly blocked from accessing the granular, raw transaction lists. 
* **Data Scale:** I assumed the dataset could grow reasonably large, which is why data aggregation for the dashboard is handled purely at the database level using `.annotate()` and `.aggregate()` rather than looping through records in Python memory.

**Tradeoffs Considered:**
* **Pure Django vs. Django REST Framework (DRF):** I consciously chose to build this using pure Django (`JsonResponse`, manual `json.loads()`) rather than using DRF.
  - *Tradeoff:* While DRF provides faster serialization and built-in JWT plugins, building the decorators, JWT decoding, and JSON responses manually demonstrates a deeper, foundational understanding of the request/response cycle, middleware concepts, and security logic.
    
* **SQLite vs. PostgreSQL:** I used SQLite as the default database.
  - *Tradeoff:* SQLite is not suitable for high-concurrency production environments. However, for the scope of this assessment, it provides a frictionless, zero-configuration setup process for the reviewer while still supporting the necessary SQL aggregation queries.
    
* **Custom JWT vs. Session Auth:** I bypassed Django's built-in session cookies to implement custom JWT authentication.
  - *Tradeoff:* This required writing a custom `@jwt_required` decorator to manually attach the user object to the request. The benefit is a fully stateless, decoupled API that is ready to be consumed by any modern frontend framework (React/Vue/Mobile).
