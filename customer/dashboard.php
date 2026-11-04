<?php
/**
 * Vehicle Service Management System
 * Customer Dashboard
 */

require_once __DIR__ . '/../config/db.php';
require_once __DIR__ . '/../includes/auth_check.php';

requireCustomer();

$userId = $_SESSION['user_id'];
$pdo = getDB();

// 1. Fetch statistics for customer
$stats = [
    'vehicles'    => 0,
    'pending'     => 0,
    'in_progress' => 0,
    'completed'   => 0
];

try {
    // Total Vehicles
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM vehicles WHERE user_id = ?");
    $stmt->execute([$userId]);
    $stats['vehicles'] = (int)$stmt->fetchColumn();

    // Requests by status
    $stmt = $pdo->prepare("
        SELECT status, COUNT(*) as count 
        FROM service_requests 
        WHERE user_id = ? 
        GROUP BY status
    ");
    $stmt->execute([$userId]);
    $statusRows = $stmt->fetchAll();
    foreach ($statusRows as $row) {
        if ($row['status'] === 'Pending') $stats['pending'] = (int)$row['count'];
        if ($row['status'] === 'In Progress') $stats['in_progress'] = (int)$row['count'];
        if ($row['status'] === 'Completed') $stats['completed'] = (int)$row['count'];
    }

    // 2. Fetch recent requests (limit 5)
    $stmt = $pdo->prepare("
        SELECT sr.*, v.brand, v.model, v.reg_number, v.vehicle_type, s.service_name, s.base_price
        FROM service_requests sr
        JOIN vehicles v ON sr.vehicle_id = v.id
        JOIN services s ON sr.service_id = s.id
        WHERE sr.user_id = ?
        ORDER BY sr.created_at DESC
        LIMIT 5
    ");
    $stmt->execute([$userId]);
    $recentRequests = $stmt->fetchAll();

    // 3. Fetch vehicles list for quick access
    $stmt = $pdo->prepare("SELECT * FROM vehicles WHERE user_id = ? ORDER BY id DESC LIMIT 4");
    $stmt->execute([$userId]);
    $userVehicles = $stmt->fetchAll();

} catch (PDOException $e) {
    setFlash('danger', 'Error loading dashboard data: ' . $e->getMessage());
    $recentRequests = [];
    $userVehicles = [];
}

$pageTitle = 'Customer Dashboard';
$activeNav = 'dashboard';
$isDashboard = true;
require_once __DIR__ . '/../includes/header.php';
?>

<div class="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
  <div>
    <h2 class="h3 fw-bold mb-1">Welcome back, <?= escape($_SESSION['user_name']) ?>! 👋</h2>
    <p class="text-muted small mb-0">Manage your fleet, book appointments, and monitor vehicle servicing in real-time.</p>
  </div>
  <div class="d-flex gap-2">
    <a href="<?= url('customer/vehicles.php') ?>" class="btn btn-outline-primary btn-sm">
      <i class="bi bi-car-front me-1"></i> Add Vehicle
    </a>
    <a href="<?= url('customer/request_service.php') ?>" class="btn btn-primary btn-sm shadow-sm">
      <i class="bi bi-calendar-plus me-1"></i> Book New Service
    </a>
  </div>
</div>

<!-- Quick Stat Cards -->
<div class="row g-3 mb-4">
  <div class="col-sm-6 col-xl-3">
    <div class="stat-card">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <div class="stat-label">My Vehicles</div>
          <div class="stat-val"><?= $stats['vehicles'] ?></div>
        </div>
        <div class="stat-icon bg-primary-subtle text-primary">
          <i class="bi bi-car-front-fill"></i>
        </div>
      </div>
    </div>
  </div>

  <div class="col-sm-6 col-xl-3">
    <div class="stat-card">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <div class="stat-label">Pending Requests</div>
          <div class="stat-val text-warning"><?= $stats['pending'] ?></div>
        </div>
        <div class="stat-icon bg-warning-subtle text-warning">
          <i class="bi bi-clock-history"></i>
        </div>
      </div>
    </div>
  </div>

  <div class="col-sm-6 col-xl-3">
    <div class="stat-card">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <div class="stat-label">In Progress</div>
          <div class="stat-val text-primary"><?= $stats['in_progress'] ?></div>
        </div>
        <div class="stat-icon bg-primary-subtle text-primary">
          <i class="bi bi-gear-wide-connected"></i>
        </div>
      </div>
    </div>
  </div>

  <div class="col-sm-6 col-xl-3">
    <div class="stat-card">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <div class="stat-label">Completed Services</div>
          <div class="stat-val text-success"><?= $stats['completed'] ?></div>
        </div>
        <div class="stat-icon bg-success-subtle text-success">
          <i class="bi bi-check-circle-fill"></i>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="row g-4">
  <!-- Recent Service Requests Table -->
  <div class="col-lg-8">
    <div class="card shadow-sm border-0 h-100">
      <div class="card-header bg-white d-flex justify-content-between align-items-center py-3">
        <h5 class="fw-bold mb-0"><i class="bi bi-clock-history text-primary me-2"></i>Recent Service Bookings</h5>
        <a href="<?= url('customer/history.php') ?>" class="text-primary small fw-semibold text-decoration-none">
          View All History <i class="bi bi-arrow-right"></i>
        </a>
      </div>

      <div class="table-responsive">
        <table class="table table-custom align-middle mb-0">
          <thead>
            <tr>
              <th>ID</th>
              <th>Vehicle</th>
              <th>Service</th>
              <th>Preferred Date</th>
              <th>Status</th>
              <th>Cost</th>
            </tr>
          </thead>
          <tbody>
            <?php if (empty($recentRequests)): ?>
              <tr>
                <td colspan="6" class="text-center py-5 text-muted">
                  <i class="bi bi-inbox fs-2 d-block mb-2 text-secondary opacity-50"></i>
                  No service requests found yet.<br>
                  <a href="<?= url('customer/request_service.php') ?>" class="btn btn-sm btn-primary mt-2">
                    <i class="bi bi-calendar-plus me-1"></i> Book Your First Service
                  </a>
                </td>
              </tr>
            <?php else: ?>
              <?php foreach ($recentRequests as $req): ?>
                <tr>
                  <td><span class="text-muted fw-bold">#<?= $req['id'] ?></span></td>
                  <td>
                    <div class="fw-bold text-dark"><?= escape($req['brand'] . ' ' . $req['model']) ?></div>
                    <span class="badge bg-light text-secondary border"><?= escape($req['reg_number']) ?></span>
                  </td>
                  <td>
                    <div class="fw-semibold"><?= escape($req['service_name']) ?></div>
                  </td>
                  <td><?= formatDate($req['preferred_date']) ?></td>
                  <td><?= statusBadge($req['status']) ?></td>
                  <td class="fw-bold text-dark">
                    <?= $req['cost'] !== null ? formatCurrency($req['cost']) : '<span class="text-muted small">Est. ' . formatCurrency($req['base_price']) . '</span>' ?>
                  </td>
                </tr>
              <?php endforeach; ?>
            <?php endif; ?>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- My Vehicles Quick Overview -->
  <div class="col-lg-4">
    <div class="card shadow-sm border-0 h-100">
      <div class="card-header bg-white d-flex justify-content-between align-items-center py-3">
        <h5 class="fw-bold mb-0"><i class="bi bi-car-front-fill text-primary me-2"></i>My Registered Fleet</h5>
        <a href="<?= url('customer/vehicles.php') ?>" class="text-primary small fw-semibold text-decoration-none">
          Manage <i class="bi bi-arrow-right"></i>
        </a>
      </div>

      <div class="card-body p-3">
        <?php if (empty($userVehicles)): ?>
          <div class="text-center py-4 text-muted">
            <i class="bi bi-car-front fs-2 d-block mb-2 text-secondary opacity-50"></i>
            No vehicles registered yet.<br>
            <a href="<?= url('customer/vehicles.php') ?>" class="btn btn-sm btn-outline-primary mt-2">
              <i class="bi bi-plus-circle me-1"></i> Add Your Vehicle
            </a>
          </div>
        <?php else: ?>
          <div class="d-flex flex-column gap-2">
            <?php foreach ($userVehicles as $veh): ?>
              <div class="p-3 border rounded-3 bg-light d-flex justify-content-between align-items-center">
                <div>
                  <div class="fw-bold text-dark"><?= escape($veh['brand'] . ' ' . $veh['model']) ?></div>
                  <div class="small text-muted d-flex align-items-center gap-2 mt-1">
                    <span class="badge bg-white text-dark border"><?= escape($veh['reg_number']) ?></span>
                    <span><?= escape($veh['fuel_type']) ?></span>
                    <span>&bull;</span>
                    <span><?= escape($veh['year']) ?></span>
                  </div>
                </div>
                <span class="badge bg-primary-subtle text-primary border border-primary-subtle">
                  <?= escape($veh['vehicle_type']) ?>
                </span>
              </div>
            <?php endforeach; ?>
          </div>
          <div class="mt-3">
            <a href="<?= url('customer/request_service.php') ?>" class="btn btn-outline-primary btn-sm w-100">
              <i class="bi bi-calendar-check me-1"></i> Schedule Service for a Vehicle
            </a>
          </div>
        <?php endif; ?>
      </div>
    </div>
  </div>
</div>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
