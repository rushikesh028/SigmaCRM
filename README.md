# SigmaCRM
### Smart Customer Relationship & Sales Management Platform

<p align="center">
  <strong>One Platform. Every Customer. Smarter Business Decisions.</strong>
  <br>
  A centralized CRM solution to manage leads, customers, sales pipelines, teams, and business performance.
</p>

---

## 📸 Application Preview

<p align="center">
  <img src="screenshots/dashboard.png" width="95%" alt="SigmaCRM Dashboard Preview">
  <br>
  <em>Dashboard – Business Overview & Analytics</em>
</p>

### Explore SigmaCRM

| Module | Preview |
|---|---|
| Lead Management | ![Leads](screenshots/leads.png) |
| Deal Management | ![Deals](screenshots/deals.png) |
| Contact Management | ![Contacts](screenshots/contacts.png) |
| Task Management | ![Tasks](screenshots/tasks.png) |
| Reports & Analytics | ![Reports](screenshots/reports.png) |

> **Note:** The images above are sample screenshot placeholders. Replace them with actual screenshots captured from your running application.

---

## 📌 About SigmaCRM

**SigmaCRM** is a modern Customer Relationship Management application developed using Python, Django, Bootstrap 5, JavaScript, Chart.js, and MySQL.

The platform is designed to simplify business operations by providing a centralized system for managing customer relationships, tracking sales opportunities, organizing business activities, and monitoring employee performance.

From lead generation to successful deal closure, SigmaCRM helps businesses maintain visibility over their entire sales process.

### 🎯 Project Objectives

- Centralize customer and lead information.
- Improve sales pipeline visibility.
- Simplify employee task management.
- Monitor business performance through analytics.
- Improve customer relationship management.
- Provide secure, role-based access to business information.

---

## ✨ Key Features

### 📊 1. Interactive Dashboard

- Business performance overview.
- Key performance indicators (KPIs).
- Lead generation trends.
- Lead source distribution.
- Deals categorized by sales stage.
- Recent activities and upcoming tasks.

### 🎯 2. Lead Management

- Complete lead CRUD operations.
- Search and filter leads.
- Filter by status, source, and assigned employee.
- Pagination for large lead databases.
- Individual lead detail pages.
- Notes and activity history.

### 💼 3. Deal Management

- Interactive Kanban sales pipeline.
- Drag-and-drop deal stage updates.
- Track sales opportunities.
- Monitor deal progression.

**Sales Pipeline:**

`New → In Progress → Proposal → Negotiation → Won / Lost`

### 👥 4. Contact Management

- Create and manage customer contacts.
- Update and delete contact records.
- Search customer information.
- Maintain centralized customer records.

### ✅ 5. Task Management

- Assign tasks to employees.
- Set task priorities.
- Configure due dates.
- Monitor overdue tasks.
- Track pending and completed activities.

### 📈 6. Reports & Analytics

Interactive business reports powered by Chart.js.

- Lead conversion analysis.
- Revenue tracking.
- Lead source performance.
- Sales funnel visualization.
- Monthly sales analysis.
- Employee performance reports.

### 🔐 7. Authentication & User Management

- Django session-based authentication.
- CSRF protection.
- Role-based access control.
- Admin-only user management.
- Separate Admin and Employee roles.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Backend framework |
| Bootstrap 5 | Responsive user interface |
| HTML5 | Frontend structure |
| CSS3 | Styling |
| JavaScript | Frontend interactions |
| Chart.js | Data visualization |
| SQLite | Local development database |
| MySQL | Production database |
| Django Authentication | Authentication and authorization |

---

## 🏗️ Project Architecture

```text
SigmaCRM/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── crm/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── admin.py
│   └── urls.py
│
├── templates/
│   └── CRM HTML templates
│
├── static/
│   ├── css/
│   └── js/
│
├── screenshots/
│   ├── dashboard.png
│   ├── leads.png
│   ├── deals.png
│   ├── contacts.png
│   ├── tasks.png
│   └── reports.png
│
├── manage.py
├── requirements.txt
├── seed_data.py
└── README.md
```

---

## ⚙️ Installation & Setup

Follow these steps to run SigmaCRM locally.

### Prerequisites

Make sure you have installed:

- Python 3.10+
- pip
- Git
- MySQL (optional, for MySQL configuration)

### Step 1: Clone the Repository

```bash
git clone https://github.com/rushikesh028/SigmaCRM.git
```

```bash
cd SigmaCRM
```

### Step 2: Create a Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Apply Database Migrations

```bash
python manage.py migrate
```

### Step 5: Create an Administrator Account

```bash
python manage.py createsuperuser
```

Follow the instructions to configure your administrator credentials.

### Step 6: Load Sample Data (Optional)

```bash
python manage.py shell < seed_data.py
```

Run this if the sample-data script is available and configured to create demo records.

### Step 7: Start the Development Server

```bash
python manage.py runserver
```

Open your browser:

**http://127.0.0.1:8000/**

---

## 🔑 Demo Credentials

If the sample-data script creates the demo accounts, use:

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Employee | `employee` | `employee123` |

> **Security Notice:** These credentials are intended for local demonstration only. Change them before deploying the application publicly.

---

## 🗄️ MySQL Database Configuration

SigmaCRM supports MySQL for production environments.

### Step 1: Create a Database

```sql
CREATE DATABASE sigmacrm
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

### Step 2: Configure Environment Variables

```bash
export USE_MYSQL=True
export MYSQL_DATABASE=sigmacrm
export MYSQL_USER=root
export MYSQL_PASSWORD=yourpassword
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
```

For Windows PowerShell, use:

```powershell
$env:USE_MYSQL="True"
$env:MYSQL_DATABASE="sigmacrm"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="yourpassword"
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3306
