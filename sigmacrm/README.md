# SigmaCRM

Professional CRM built with Python, Django, Bootstrap 5, Chart.js and MySQL (SQLite for local demo).

## Features

- **Dashboard** — Live KPIs, leads over time, source breakdown, deals by stage, activities & tasks
- **Leads** — Full CRUD, search, filter by status/source/assignee, pagination, detail page with notes & activity log
- **Deals** — Kanban pipeline (New → In Progress → Proposal → Negotiation → Won/Lost) with drag-and-drop stage updates
- **Contacts** — CRUD + search
- **Tasks** — Assignment, priorities, due dates, overdue tracking, complete toggle
- **Reports** — Conversion, revenue, sources, funnel, monthly sales, employee performance (Chart.js)
- **Users** — Admin-only user management, roles (Admin / Employee)
- **Auth** — Django session auth, CSRF, role-based access

## Quick Start (SQLite — recommended for first run)

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # or use seeded admin/admin123 after seed
python manage.py runserver
```

Open http://127.0.0.1:8000/

**Demo logins (after seeding):**
- Admin: `admin` / `admin123`
- Employee: `employee` / `employee123`

### Seed sample data

```bash
python manage.py shell < seed_data.py
# or run the seed script once (see below)
```

## MySQL (production)

1. Create database:
   ```sql
   CREATE DATABASE sigmacrm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. Set environment variables (or export before run):
   ```bash
   export USE_MYSQL=True
   export MYSQL_DATABASE=sigmacrm
   export MYSQL_USER=root
   export MYSQL_PASSWORD=yourpassword
   export MYSQL_HOST=127.0.0.1
   export MYSQL_PORT=3306
   ```

3. Install system deps (Ubuntu):
   ```bash
   sudo apt-get install default-libmysqlclient-dev pkg-config build-essential
   pip install mysqlclient
   ```

4. Migrate and run:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Project structure

```
sigmacrm/
  manage.py
  config/          # settings, urls, wsgi
  crm/             # models, views, forms, admin, urls
  templates/       # Django templates
  static/css|js    # styles and app JS
  requirements.txt
  README.md
```

## Default roles

- **Admin** — full access including Users menu
- **Employee** — all CRM modules except user management

## License

MIT — use freely for learning and production.
