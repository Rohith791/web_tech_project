<?php
/**
 * Vehicle Service Management System
 * Global Header Template
 */

require_once __DIR__ . '/../config/db.php';
require_once __DIR__ . '/auth_check.php';

$pageTitle = $pageTitle ?? 'Vehicle Service Management System';
$isDashboard = $isDashboard ?? false;
$activeNav = $activeNav ?? '';
$user = $_SESSION['user_name'] ?? null;
$role = $_SESSION['user_role'] ?? null;
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Vehicle Service Management System - High performance maintenance, booking, and fleet management.">
  <title><?= escape($pageTitle) ?> | VSM System</title>
  
  <!-- Bootstrap 5 CSS CDN -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
  <!-- Bootstrap Icons CDN -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <!-- Custom Modern Stylesheet -->
  <link rel="stylesheet" href="<?= url('assets/css/style.css') ?>">
</head>
<body>

<?php if (!$isDashboard): ?>
  <!-- Public Top Navigation -->
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark py-3 border-bottom border-secondary border-opacity-25 sticky-top shadow-sm">
    <div class="container">
      <a class="navbar-brand d-flex align-items-center gap-2 fw-bold fs-4 text-white" href="<?= url('index.php') ?>">
        <span class="p-2 rounded-3 bg-primary text-white d-inline-flex align-items-center justify-content-center shadow-sm" style="width: 38px; height: 38px;">
          <i class="bi bi-tools fs-5"></i>
        </span>
        <span>VSM <span class="text-primary-light text-primary">Pro</span></span>
      </a>
      
      <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarPublic" aria-controls="navbarPublic" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarPublic">
        <ul class="navbar-nav ms-auto align-items-lg-center gap-2 pt-3 pt-lg-0">
          <li class="nav-item">
            <a class="nav-link text-white-50 <?= $activeNav === 'home' ? 'text-white fw-bold active' : '' ?>" href="<?= url('index.php') ?>">
              <i class="bi bi-house-door me-1"></i> Home
            </a>
          </li>
          
          <?php if (isLoggedIn()): ?>
            <li class="nav-item">
              <a class="nav-link text-white-50" href="<?= isAdmin() ? url('admin/dashboard.php') : url('customer/dashboard.php') ?>">
                <i class="bi bi-speedometer2 me-1"></i> <?= isAdmin() ? 'Admin Portal' : 'My Dashboard' ?>
              </a>
            </li>
            <li class="nav-item ms-lg-2">
              <a href="<?= url('auth/logout.php') ?>" class="btn btn-outline-light btn-sm px-3">
                <i class="bi bi-box-arrow-right me-1"></i> Sign Out
              </a>
            </li>
          <?php else: ?>
            <li class="nav-item ms-lg-2">
              <a class="btn btn-outline-light btn-sm px-3" href="<?= url('auth/login.php') ?>">
                <i class="bi bi-box-arrow-in-right me-1"></i> Sign In
              </a>
            </li>
            <li class="nav-item">
              <a class="btn btn-primary btn-sm px-3 shadow-sm" href="<?= url('auth/register.php') ?>">
                <i class="bi bi-person-plus-fill me-1"></i> Register Free
              </a>
            </li>
          <?php endif; ?>
        </ul>
      </div>
    </div>
  </nav>

  <!-- Flash Alerts for Public Pages -->
  <div class="container mt-3">
    <?php displayFlash(); ?>
  </div>

<?php else: ?>
  <!-- Dashboard Top Mobile Navbar & Layout -->
  <header class="navbar navbar-dark bg-dark sticky-top p-2 p-md-3 border-bottom border-secondary border-opacity-25 shadow-sm d-lg-none">
    <div class="container-fluid">
      <button class="btn btn-outline-light btn-sm me-2" id="sidebarToggle" type="button" aria-label="Toggle Sidebar">
        <i class="bi bi-list fs-5"></i>
      </button>
      <a class="navbar-brand d-flex align-items-center gap-2 fw-bold text-white fs-5 me-auto" href="#">
        <i class="bi bi-wrench-adjustable-circle text-primary"></i> VSM Pro
      </a>
      <a href="<?= url('auth/logout.php') ?>" class="btn btn-outline-danger btn-sm">
        <i class="bi bi-box-arrow-right"></i>
      </a>
    </div>
  </header>

  <div class="sidebar-overlay"></div>

  <div class="dashboard-wrapper">
    <!-- Sidebar Navigation -->
    <aside class="sidebar">
      <a class="sidebar-brand" href="<?= url('index.php') ?>">
        <span class="p-2 rounded-3 bg-primary text-white d-inline-flex align-items-center justify-content-center shadow-sm" style="width: 36px; height: 36px;">
          <i class="bi bi-tools fs-6"></i>
        </span>
        <div class="lh-sm">
          <div>VSM Pro</div>
          <small class="text-white-50 fw-normal fs-6 text-uppercase" style="font-size: 0.65rem !important; letter-spacing: 0.08em;">
            <?= isAdmin() ? 'Admin Portal' : 'Customer Suite' ?>
          </small>
        </div>
      </a>

      <ul class="sidebar-nav">
        <?php if (isCustomer()): ?>
          <li class="nav-heading">Main Navigation</li>
          <li>
            <a href="<?= url('customer/dashboard.php') ?>" class="sidebar-link <?= $activeNav === 'dashboard' ? 'active' : '' ?>">
              <i class="bi bi-grid-1x2-fill"></i>
              <span>Dashboard</span>
            </a>
          </li>
          <li>
            <a href="<?= url('customer/vehicles.php') ?>" class="sidebar-link <?= $activeNav === 'vehicles' ? 'active' : '' ?>">
              <i class="bi bi-car-front-fill"></i>
              <span>My Vehicles</span>
            </a>
          </li>
          <li>
            <a href="<?= url('customer/request_service.php') ?>" class="sidebar-link <?= $activeNav === 'request_service' ? 'active' : '' ?>">
              <i class="bi bi-calendar-plus-fill"></i>
              <span>Book Service</span>
            </a>
          </li>
          <li>
            <a href="<?= url('customer/history.php') ?>" class="sidebar-link <?= $activeNav === 'history' ? 'active' : '' ?>">
              <i class="bi bi-clock-history"></i>
              <span>Service History</span>
            </a>
          </li>
        <?php elseif (isAdmin()): ?>
          <li class="nav-heading">Administration</li>
          <li>
            <a href="<?= url('admin/dashboard.php') ?>" class="sidebar-link <?= $activeNav === 'admin_dashboard' ? 'active' : '' ?>">
              <i class="bi bi-pie-chart-fill"></i>
              <span>Overview</span>
            </a>
          </li>
          <li>
            <a href="<?= url('admin/requests.php') ?>" class="sidebar-link <?= $activeNav === 'admin_requests' ? 'active' : '' ?>">
              <i class="bi bi-clipboard2-check-fill"></i>
              <span>Service Requests</span>
            </a>
          </li>
          <li>
            <a href="<?= url('admin/customers.php') ?>" class="sidebar-link <?= $activeNav === 'admin_customers' ? 'active' : '' ?>">
              <i class="bi bi-people-fill"></i>
              <span>Customers & Fleet</span>
            </a>
          </li>
        <?php endif; ?>

        <li class="nav-heading mt-3">Quick Links</li>
        <li>
          <a href="<?= url('index.php') ?>" class="sidebar-link">
            <i class="bi bi-globe2"></i>
            <span>Public Home</span>
          </a>
        </li>
      </ul>

      <!-- Sidebar User Profile Info & Sign Out -->
      <div class="sidebar-user">
        <div class="user-card mb-2">
          <div class="avatar-circle">
            <?= strtoupper(substr($user ?? 'U', 0, 1)) ?>
          </div>
          <div class="lh-sm overflow-hidden">
            <div class="text-white fw-bold text-truncate" style="font-size: 0.875rem;">
              <?= escape($user ?? 'User') ?>
            </div>
            <span class="badge bg-<?= isAdmin() ? 'danger' : 'primary' ?>-subtle text-<?= isAdmin() ? 'danger' : 'primary' ?>-emphasis" style="font-size: 0.65rem;">
              <?= strtoupper($role ?? 'GUEST') ?>
            </span>
          </div>
        </div>
        <a href="<?= url('auth/logout.php') ?>" class="btn btn-outline-danger btn-sm w-100 d-flex align-items-center justify-content-center gap-2">
          <i class="bi bi-box-arrow-right"></i> Sign Out
        </a>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="dashboard-main">
      <!-- Flash Alert in Dashboard -->
      <?php displayFlash(); ?>
<?php endif; ?>
