<?php
/**
 * Vehicle Service Management System
 * Administrator Dashboard Overview
 */

require_once __DIR__ . '/../config/db.php';
require_once __DIR__ . '/../includes/auth_check.php';

requireAdmin();

$pdo = getDB();

$stats = [
    'customers'   => 0,
    'vehicles'    => 0,
    'pending'     => 0,
    'in_progress' => 0,
    'completed'   => 0,
    'cancelled'   => 0,
    'revenue'     => 0.00
];

try {
    // Total Customers
    $stmt = $pdo->query("SELECT COUNT(*) FROM users WHERE role = 'customer'");
    $stats['customers'] = (int)$stmt->fetchColumn();

    // Total Vehicles
    $stmt = $pdo->query("SELECT COUNT(*) FROM vehicles");
    $stats['vehicles'] = (int)$stmt->fetchColumn();

    // Requests count by status
    $stmt = $pdo->query("SELECT status, COUNT(*) as count FROM service_requests GROUP BY status");
    $rows = $stmt->fetchAll();
    foreach ($rows as $r) {
        if ($r['status'] === 'Pending') $stats['pending'] = (int)$r['count'];
        if ($r['status'] === 'In Progress') $stats['in_progress'] = (int)$r['count'];
        if ($r['status'] === 'Completed') $stats['completed'] = (int)$r['count'];
        if ($r['status'] === 'Cancelled') $stats['cancelled'] = (int)$r['count'];
    }

    // Revenue from completed services
    $stmt = $pdo->query("SELECT COALESCE(SUM(cost), 0) FROM service_requests WHERE status = 'Completed'");
    $stats['revenue'] = (float)$stmt->fetchColumn();

    // Recent 6 Service Requests
    $stmt = $pdo->query("
        SELECT sr.*, 
               u.name as customer_name, u.email as customer_email, u.phone as customer_phone,
               v.brand, v.model, v.reg_number,
               s.service_name, s.base_price
        FROM service_requests sr
        JOIN users u ON sr.user_id = u.id
        JOIN vehicles v ON sr.vehicle_id = v.id
        JOIN services s ON sr.service_id = s.id
        ORDER BY sr.id DESC
        LIMIT 6
    ");
    $recentRequests = $stmt->fetchAll();

} catch (PDOException $e) {
    setFlash('danger', 'Error reading administrator metrics: ' . $e->getMessage());
    $recentRequests = [];
}

$pageTitle = 'Admin Dashboard';
$activeNav = 'admin_dashboard';
$isDashboard = true;
require_once __DIR__ . '/../includes/header.php';
?>

<div class="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
  <div>
    <h2 class="h3 fw-bold mb-1"><i class="bi bi-shield-check text-primary me-2"></i>Admin Management Console</h2>
    <p class="text-muted small mb-0">Live operations overview, fleet metrics, and service queue status.</p>
  </div>
  <div class="d-flex gap-2">
    <a href="<?= url('admin/requests.php') ?>" class="btn btn-primary btn-sm shadow-sm">
      <i class="bi bi-clipboard2-check me-1"></i> Manage Requests
    </a>
    <a href="<?= url('admin/customers.php') ?>" class="btn btn-outline-dark btn-sm">
      <i class="bi bi-people me-1"></i> Customer Directory
    </a>
  </div>
</div>

<!-- 5 Summary KPI Cards -->
<div class="row g-3 mb-4">
  <!-- Total Customers -->
  <div class="col-sm-6 col-xl-4 col-xxl-2">
    <div class="stat-card">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <div class="stat-label">Total Customers</div>
          <div class="stat-val text-dark"><?= $stats['customers'] ?></div>
        </div>
        <div class="stat-icon bg-primary-subtle text-primary">
          <i class="bi bi-people-fill"></i>
        </div>
      </div>
    </div>
  </div>

  <!-- Total Vehicles -->
  <div class="col-sm-6 col-xl-4 col-xxl-2">
    <div class="stat-card">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <div class="stat-label">Total Vehicles</div>
          <div class="stat-val text-dark"><?= $stats['vehicles'] ?></div>
        </div>
        <div class="stat-icon bg-info-subtle text-info-emphasis">
          <i class="bi bi-car-front-fill"></i>
        </div>
      </div>
    </div>
  </div>

  <!-- Pending Requests -->
  <div class="col-sm-6 col-xl-4 col-xxl-2">
    <div class="stat-card">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <div class="stat-label">Pending</div>
          <div class="stat-val text-warning"><?= $stats['pending'] ?></div>
        </div>
        <div class="stat-icon bg-warning-subtle text-warning">
          <i class="bi bi-clock-history"></i>
        </div>
      </div>
    </div>
  </div>

  <!-- In Progress Requests -->
  <div class="col-sm-6 col-xl-4 col-xxl-2">
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

  <!-- Completed Requests -->
  <div class="col-sm-6 col-xl-4 col-xxl-2">
    <div class="stat-card">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <div class="stat-label">Completed</div>
          <div class="stat-val text-success"><?= $stats['completed'] ?></div>
        </div>
        <div class="stat-icon bg-success-subtle text-success">
          <i class="bi bi-check-circle-fill"></i>
        </div>
      </div>
    </div>
  </div>

  <!-- Total Completed Revenue -->
  <div class="col-sm-6 col-xl-4 col-xxl-2">
    <div class="stat-card">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <div class="stat-label">Total Revenue</div>
          <div class="stat-val text-success" style="font-size: 1.55rem;"><?= formatCurrency($stats['revenue']) ?></div>
        </div>
        <div class="stat-icon bg-success-subtle text-success">
          <i class="bi bi-currency-dollar"></i>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Recent Queue Management -->
<div class="card shadow-sm border-0 mb-4">
  <div class="card-header bg-white d-flex justify-content-between align-items-center py-3">
    <div class="d-flex align-items-center gap-2">
      <i class="bi bi-list-check text-primary fs-5"></i>
      <h5 class="fw-bold mb-0 text-dark">Recent Service Requests</h5>
    </div>
    <a href="<?= url('admin/requests.php') ?>" class="btn btn-outline-primary btn-sm">
      View All Requests & Update Status <i class="bi bi-arrow-right"></i>
    </a>
  </div>

  <div class="table-responsive">
    <table class="table table-custom align-middle mb-0">
      <thead>
        <tr>
          <th>Req ID</th>
          <th>Customer</th>
          <th>Vehicle</th>
          <th>Service Package</th>
          <th>Preferred Date</th>
          <th>Status</th>
          <th>Cost</th>
          <th class="text-end">Action</th>
        </tr>
      </thead>
      <tbody>
        <?php if (empty($recentRequests)): ?>
          <tr>
            <td colspan="8" class="text-center py-5 text-muted">
              <i class="bi bi-inbox fs-2 opacity-50 d-block mb-2"></i>
              No service requests created in the system yet.
            </td>
          </tr>
        <?php else: ?>
          <?php foreach ($recentRequests as $req): ?>
            <tr>
              <td><span class="fw-bold font-monospace text-primary">#<?= $req['id'] ?></span></td>
              <td>
                <div class="fw-bold text-dark"><?= escape($req['customer_name']) ?></div>
                <div class="small text-muted"><?= escape($req['customer_phone']) ?></div>
              </td>
              <td>
                <div class="fw-semibold text-dark"><?= escape($req['brand'] . ' ' . $req['model']) ?></div>
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
              <td class="text-end">
                <a href="<?= url('admin/requests.php?req_id=' . $req['id']) ?>" class="btn btn-sm btn-primary">
                  <i class="bi bi-pencil-square me-1"></i> Manage
                </a>
              </td>
            </tr>
          <?php endforeach; ?>
        <?php endif; ?>
      </tbody>
    </table>
  </div>
</div>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
