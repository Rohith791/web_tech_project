<?php
/**
 * Vehicle Service Management System
 * Public Landing Page
 */

require_once __DIR__ . '/config/db.php';

$pdo = getDB();
$services = [];
try {
    $stmt = $pdo->query("SELECT * FROM services ORDER BY id ASC");
    $services = $stmt->fetchAll();
} catch (PDOException $e) {
    $services = [];
}

$pageTitle = 'Home - Professional Auto Care & Service Management';
$activeNav = 'home';
$isDashboard = false;
require_once __DIR__ . '/includes/header.php';
?>

<!-- Hero Section -->
<section class="hero-section py-5">
  <div class="container py-4">
    <div class="row align-items-center gy-4">
      <div class="col-lg-7">
        <span class="badge bg-primary bg-opacity-25 text-white border border-primary border-opacity-50 px-3 py-2 mb-3">
          <i class="bi bi-patch-check-fill text-warning me-1"></i> Trusted Auto Care & Fleet Operations
        </span>
        <h1 class="display-4 fw-extrabold text-white mb-3">
          Smart Vehicle Service, <br>
          <span class="text-primary-light" style="color: #60a5fa;">Seamless Management.</span>
        </h1>
        <p class="lead text-white-50 mb-4" style="max-width: 580px;">
          Track maintenance, schedule expert repairs, manage your fleet, and monitor live service statuses with full transparency and zero hassle.
        </p>

        <div class="d-flex flex-wrap gap-3 align-items-center">
          <?php if (isLoggedIn()): ?>
            <a href="<?= isAdmin() ? url('admin/dashboard.php') : url('customer/dashboard.php') ?>" class="btn btn-primary btn-lg px-4 shadow">
              <i class="bi bi-speedometer2 me-2"></i> Go to My Dashboard
            </a>
          <?php else: ?>
            <a href="<?= url('auth/register.php') ?>" class="btn btn-primary btn-lg px-4 shadow">
              <i class="bi bi-calendar2-check-fill me-2"></i> Book Service Now
            </a>
            <a href="<?= url('auth/login.php') ?>" class="btn btn-outline-light btn-lg px-4">
              <i class="bi bi-box-arrow-in-right me-2"></i> Customer Sign In
            </a>
          <?php endif; ?>
        </div>

        <div class="row mt-5 pt-3 border-top border-secondary border-opacity-25 text-white-50 g-4">
          <div class="col-4">
            <div class="h3 fw-bold text-white mb-0">100%</div>
            <div class="small">Transparent Pricing</div>
          </div>
          <div class="col-4">
            <div class="h3 fw-bold text-white mb-0">6+</div>
            <div class="small">Certified Services</div>
          </div>
          <div class="col-4">
            <div class="h3 fw-bold text-white mb-0">24/7</div>
            <div class="small">Online Booking</div>
          </div>
        </div>
      </div>

      <div class="col-lg-5 text-center">
        <div class="card bg-dark bg-opacity-50 border border-secondary border-opacity-50 rounded-4 p-4 shadow-lg text-start backdrop-blur">
          <div class="d-flex align-items-center justify-content-between mb-3">
            <h5 class="text-white fw-bold mb-0"><i class="bi bi-lightning-charge-fill text-warning me-2"></i> Live Fleet Tracker</h5>
            <span class="badge bg-success-subtle text-success border border-success-subtle">System Online</span>
          </div>

          <div class="p-3 bg-dark bg-opacity-75 rounded-3 mb-2 border border-secondary border-opacity-25">
            <div class="d-flex justify-content-between align-items-center small text-white-50 mb-1">
              <span>Honda Civic (ABC-1024)</span>
              <span class="badge bg-success-subtle text-success">Completed</span>
            </div>
            <div class="text-white fw-semibold small">General Service & Filter Replacement</div>
          </div>

          <div class="p-3 bg-dark bg-opacity-75 rounded-3 mb-2 border border-secondary border-opacity-25">
            <div class="d-flex justify-content-between align-items-center small text-white-50 mb-1">
              <span>Yamaha MT-15 (YAM-7788)</span>
              <span class="badge bg-primary-subtle text-primary">In Progress</span>
            </div>
            <div class="text-white fw-semibold small">Synthetic Oil & Filter Bay 3</div>
          </div>

          <div class="p-3 bg-dark bg-opacity-75 rounded-3 border border-secondary border-opacity-25">
            <div class="d-flex justify-content-between align-items-center small text-white-50 mb-1">
              <span>Tesla Model 3 (EV-9900)</span>
              <span class="badge bg-warning-subtle text-warning">Pending</span>
            </div>
            <div class="text-white fw-semibold small">Deep Foam Wash & Detailing</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Our Available Services Section -->
<section class="py-5 bg-light" id="services">
  <div class="container py-4">
    <div class="text-center max-w-600 mx-auto mb-5">
      <span class="badge bg-primary-subtle text-primary border border-primary-subtle px-3 py-2 text-uppercase fw-bold">Our Catalog</span>
      <h2 class="display-6 fw-bold mt-2">Comprehensive Vehicle Services</h2>
      <p class="text-muted">High-standard inspection, repair, and detailing performed by certified automotive technicians.</p>
    </div>

    <div class="row g-4">
      <?php 
      $icons = [
        'General Service' => 'bi-wrench-adjustable',
        'Oil & Filter Change' => 'bi-droplet-half',
        'Brake Repair & Inspection' => 'bi-shield-check',
        'Engine Diagnostics & Repair' => 'bi-cpu',
        'Complete Car Spa & Washing' => 'bi-water',
        'Tyre Replacement & Balancing' => 'bi-disc'
      ];
      foreach ($services as $srv): 
        $iconClass = $icons[$srv['service_name']] ?? 'bi-gear-fill';
      ?>
        <div class="col-md-6 col-lg-4">
          <div class="card service-card p-4 h-100 shadow-sm border">
            <div class="service-icon-box">
              <i class="bi <?= $iconClass ?>"></i>
            </div>
            <h5 class="fw-bold mb-2"><?= escape($srv['service_name']) ?></h5>
            <p class="text-muted small flex-grow-1"><?= escape($srv['description']) ?></p>
            <div class="d-flex align-items-center justify-content-between pt-3 border-top mt-2">
              <span class="text-muted small">Starting Base</span>
              <span class="fs-5 fw-bold text-primary"><?= formatCurrency($srv['base_price']) ?></span>
            </div>
          </div>
        </div>
      <?php endforeach; ?>
    </div>
  </div>
</section>

<!-- How It Works Section -->
<section class="py-5 bg-white">
  <div class="container py-4">
    <div class="text-center mb-5">
      <span class="badge bg-secondary-subtle text-secondary border px-3 py-2 text-uppercase fw-bold">Process</span>
      <h2 class="display-6 fw-bold mt-2">How VSM Pro Works</h2>
      <p class="text-muted">A fast, 3-step streamlined service experience for every vehicle owner.</p>
    </div>

    <div class="row g-4 text-center">
      <div class="col-md-4">
        <div class="p-4 rounded-4 border bg-light h-100">
          <div class="display-5 text-primary mb-3"><i class="bi bi-car-front"></i></div>
          <h5 class="fw-bold">1. Add Your Vehicles</h5>
          <p class="text-muted small mb-0">Register your car, motorcycle, SUV or truck with brand, model, year, and registration number.</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="p-4 rounded-4 border bg-light h-100">
          <div class="display-5 text-primary mb-3"><i class="bi bi-calendar2-check"></i></div>
          <h5 class="fw-bold">2. Request Service</h5>
          <p class="text-muted small mb-0">Select your vehicle, choose from our catalog of services, pick a preferred date, and submit notes.</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="p-4 rounded-4 border bg-light h-100">
          <div class="display-5 text-primary mb-3"><i class="bi bi-check-circle"></i></div>
          <h5 class="fw-bold">3. Live Status & Delivery</h5>
          <p class="text-muted small mb-0">Track real-time progress badges from Pending to In Progress to Completed with full cost transparency.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Call to Action Banner -->
<section class="py-5 bg-dark text-white text-center">
  <div class="container py-4">
    <h2 class="fw-bold text-white mb-3">Ready to schedule maintenance for your vehicle?</h2>
    <p class="text-white-50 lead mb-4">Join hundreds of satisfied customers maintaining their vehicles smoothly.</p>
    <a href="<?= url('auth/register.php') ?>" class="btn btn-primary btn-lg px-5 shadow">
      <i class="bi bi-person-plus-fill me-2"></i> Register Your Vehicle Today
    </a>
  </div>
</section>

<?php require_once __DIR__ . '/includes/footer.php'; ?>
