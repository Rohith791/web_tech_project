# Vehicle Service Management System (VSM Pro)

A modern, responsive, and secure full-stack web application for managing vehicle maintenance, customer service bookings, and workshop administration.

Built with **PHP 8 (PDO)**, **MySQL / MariaDB**, **Vanilla JavaScript**, **CSS3**, and **Bootstrap 5**.

---

## 🌟 Key Features

### 1. Customer Portal
- **User Registration & Authentication**: Secure registration with client/server validation and bcrypt password hashing.
- **Vehicle Fleet Management**: Add, view, edit, and delete vehicles with brand, model, registration number, year, fuel type, and vehicle type.
- **Service Booking**: Schedule appointments by choosing from available services (General Service, Oil Change, Brake Repair, etc.), picking preferred dates, adding notes, and viewing live pricing estimates.
- **Service Request History**: Real-time status tracking (`Pending`, `In Progress`, `Completed`, `Cancelled`), workshop notes/remarks, itemized billing cost, and instant cancellation of pending bookings.

### 2. Admin Management Suite
- **Interactive Overview Dashboard**: Key metrics summary cards (Total Customers, Fleet Size, Pending, In-Progress, Completed requests, and Total Revenue).
- **Service Request Queue**: Comprehensive filterable and searchable view of all incoming service tickets with customer and vehicle details.
- **Ticket Status & Cost Updates**: Modal interface to update status, enter diagnostic/technician remarks, and assign finalized repair costs.
- **Customer & Fleet Directory**: Searchable registry of all customer accounts with full fleet breakdown and service statistics.

### 3. Security & Architecture
- **PDO Prepared Statements**: 100% parameter binding on all queries to prevent SQL Injection.
- **XSS Protection**: Complete HTML escaping (`htmlspecialchars` with `ENT_QUOTES`).
- **CSRF Tokens**: Form security verification across state-altering actions.
- **Role-Based Access Control (RBAC)**: Strict separation of admin and customer access levels.
- **Data Integrity**: Foreign keys with `ON DELETE CASCADE` and unique vehicle registration constraints.

---

## 🗄️ Database Structure

Database name: `vehicle_service_db`

- `users` (id, name, email UNIQUE, phone, password_hash, address, role ENUM('customer','admin'), created_at)
- `vehicles` (id, user_id FK, vehicle_type, brand, model, reg_number UNIQUE, year, fuel_type, created_at)
- `services` (id, service_name, description, base_price, created_at)
- `service_requests` (id, user_id FK, vehicle_id FK, service_id FK, preferred_date, description, status ENUM('Pending','In Progress','Completed','Cancelled'), admin_remark, cost, created_at, updated_at)

---

## 🔑 Default Seeded Accounts

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@vsm.com` | `admin123` | System Administrator |
| **Customer** | `john@example.com` | `customer123` | John Doe (Has Civic & Yamaha MT-15) |
| **Customer** | `sarah@example.com` | `customer123` | Sarah Connor (Has Tesla Model 3 & RAV4) |

---

## 🚀 Setup & Installation Instructions (XAMPP)

### Step 1: Start XAMPP Services
1. Launch **XAMPP Control Panel**.
2. Start both **Apache** and **MySQL**.

### Step 2: Import the Database
1. Open **phpMyAdmin** at `http://localhost/phpmyadmin` (or use MySQL command line).
2. Create a new database named `vehicle_service_db`.
3. Import the schema file located at:
   ```
   database/schema.sql
   ```
   *Alternative via Terminal:*
   ```bash
   mysql -u root -p vehicle_service_db < database/schema.sql
   ```

### Step 3: Configure Database Connection
Edit `config/db.php` if your local MySQL user/password differs from standard XAMPP defaults:
```php
define('DB_HOST', '127.0.0.1');
define('DB_NAME', 'vehicle_service_db');
define('DB_USER', 'root');
define('DB_PASS', ''); // default is empty in XAMPP
```

### Step 4: Run the Application

#### Option A: Running via XAMPP Apache
Place the project folder in `C:\xampp\htdocs\vehicle-service-system`, then access:
```
http://localhost/vehicle-service-system/
```

#### Option B: Running via PHP Built-in Server
From the root of this project folder, run:
```bash
php -S localhost:8000
```
Then navigate to:
```
http://localhost:8000/
```

---

## 📁 Project File Structure

```
vehicle-service-system/
├── index.php                 # Public landing page with service catalog & CTA
├── config/
│   └── db.php                # PDO connection, URL helpers, flash alerts, and security functions
├── auth/
│   ├── register.php          # Customer registration with validation
│   ├── login.php             # Unified secure login with role redirection
│   └── logout.php            # Session destruction and cookie purge
├── customer/
│   ├── dashboard.php         # Customer metrics, recent bookings & fleet summary
│   ├── vehicles.php          # Vehicle management (Add, View, Edit, Delete)
│   ├── request_service.php   # Schedule service appointment with live estimate
│   └── history.php           # Service history, status filters & pending cancellation
├── admin/
│   ├── dashboard.php         # Workshop KPI metrics, status cards & revenue
│   ├── requests.php          # Manage requests, update status, remarks & billing cost
│   └── customers.php         # Customer registry with vehicle fleet inspector
├── includes/
│   ├── header.php            # Responsive topbar & sidebar navigation
│   ├── footer.php            # Global confirmation modal & script inclusions
│   └── auth_check.php        # Role guards (requireLogin, requireAdmin, requireCustomer, CSRF)
├── assets/
│   ├── css/
│   │   └── style.css         # Modern styling, custom components, typography & themes
│   └── js/
│       ├── validation.js     # Form validation (regex, phone, password, year, date)
│       └── main.js           # Live table search/filtering, sidebar toggle & modal bindings
├── database/
│   └── schema.sql            # Table definitions, foreign keys, indexes & seed data
└── README.md                 # Setup guide, credentials & project overview
```
