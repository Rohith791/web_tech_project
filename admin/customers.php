<?php
/**
 * Vehicle Service Management System
 * Admin Customer Management & Fleet Overview
 */

require_once __DIR__ . '/../config/db.php';
require_once __DIR__ . '/../includes/auth_check.php';

requireAdmin();

$pdo = getDB();

// Fetch all customers with vehicle count and request count
$stmt = $pdo->query("
    SELECT u.*,
           COUNT(DISTINCT v.id) as vehicle_count,
           COUNT(DISTINCT sr.id) as request_count
    FROM users u
    LEFT JOIN vehicles v ON u.id = v.user_id
    LEFT JOIN service_requests sr ON u.id = sr.user_id
    WHERE u.role = 'customer'
    GROUP BY u.id
    ORDER BY u.id DESC
");
$customers = $stmt->fetchAll();

// Pre-fetch all vehicles grouped by user_id for customer modals
$stmt = $pdo->query("SELECT * FROM vehicles ORDER BY id DESC");
$allVehicles = $stmt->fetchAll();
$vehiclesByUser = [];
foreach ($allVehicles as $v) {
    $vehiclesByUser[$v['user_id']][] = $v;
}

$pageTitle = 'Registered Customers & Fleet';
$activeNav = 'admin_customers';
$isDashboard = true;
require_once __DIR__ . '/../includes/header.php';
?>

<div class="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
  <div>
    <h2 class="h3 fw-bold mb-1"><i class="bi bi-people-fill text-primary me-2"></i>Customer Directory & Fleet</h2>
    <p class="text-muted small mb-0">Browse all registered client accounts, contact information, and associated vehicle fleets.</p>
  </div>
  <div class="text-muted small">
    Total Clients: <span class="fw-bold text-dark fs-6"><?= count($customers) ?></span>
  </div>
</div>

<!-- Search Bar -->
<div class="card border-0 shadow-sm mb-4">
  <div class="card-body p-3">
    <div class="row g-3 align-items-center">
      <div class="col-md-8">
        <div class="input-group">
          <span class="input-group-text bg-light border-end-0"><i class="bi bi-search text-muted"></i></span>
          <input type="text" class="form-control border-start-0" data-table-search="customersTable" placeholder="Search customer by name, email, phone number, address...">
        </div>
      </div>
      <div class="col-md-4 text-md-end text-muted small">
        <i class="bi bi-shield-check text-success me-1"></i> Verified Active Accounts
      </div>
    </div>
  </div>
</div>

<!-- Customers Table -->
<div class="card shadow-sm border-0">
  <div class="table-responsive">
    <table class="table table-custom align-middle mb-0" id="customersTable">
      <thead>
        <tr>
          <th>Customer</th>
          <th>Contact Info</th>
          <th>Address</th>
          <th>Fleet Size</th>
          <th>Total Requests</th>
          <th>Registered On</th>
          <th class="text-end">Fleet Details</th>
        </tr>
      </thead>
      <tbody>
        <?php if (empty($customers)): ?>
          <tr class="no-filter">
            <td colspan="7" class="text-center py-5 text-muted">
              <i class="bi bi-people fs-1 text-secondary opacity-50 d-block mb-3"></i>
              No customers registered yet.
            </td>
          </tr>
        <?php else: ?>
          <?php foreach ($customers as $c): 
            $custVehicles = $vehiclesByUser[$c['id']] ?? [];
          ?>
            <tr>
              <td>
                <div class="d-flex align-items-center gap-3">
                  <div class="avatar-circle">
                    <?= strtoupper(substr($c['name'], 0, 1)) ?>
                  </div>
                  <div>
                    <div class="fw-bold text-dark fs-6"><?= escape($c['name']) ?></div>
                    <small class="text-muted">Customer ID #<?= $c['id'] ?></small>
                  </div>
                </div>
              </td>
              <td>
                <div class="fw-semibold text-dark"><i class="bi bi-envelope me-1 text-primary"></i><?= escape($c['email']) ?></div>
                <div class="small text-muted"><i class="bi bi-telephone me-1 text-secondary"></i><?= escape($c['phone']) ?></div>
              </td>
              <td>
                <div class="small text-secondary" style="max-width: 220px;">
                  <?= escape($c['address'] ?: 'No address specified') ?>
                </div>
              </td>
              <td>
                <span class="badge bg-primary-subtle text-primary border border-primary-subtle fs-6 px-2 py-1">
                  <i class="bi bi-car-front-fill me-1"></i><?= $c['vehicle_count'] ?>
                </span>
              </td>
              <td>
                <span class="badge bg-light text-dark border fs-6 px-2 py-1">
                  <i class="bi bi-clipboard2-check me-1 text-secondary"></i><?= $c['request_count'] ?>
                </span>
              </td>
              <td class="text-muted small">
                <?= formatDate($c['created_at']) ?>
              </td>
              <td class="text-end">
                <button type="button" class="btn btn-sm btn-outline-primary view-fleet-btn"
                        data-bs-toggle="modal"
                        data-bs-target="#customerFleetModal"
                        data-name="<?= escape($c['name']) ?>"
                        data-email="<?= escape($c['email']) ?>"
                        data-phone="<?= escape($c['phone']) ?>"
                        data-vehicles='<?= htmlspecialchars(json_encode($custVehicles), ENT_QUOTES, 'UTF-8') ?>'
                        title="View Fleet">
                  <i class="bi bi-car-front me-1"></i> View Fleet (<?= count($custVehicles) ?>)
                </button>
              </td>
            </tr>
          <?php endforeach; ?>
          <tr class="empty-filter-row" style="display: none;">
            <td colspan="7" class="text-center py-4 text-muted">
              <i class="bi bi-search me-1"></i> No customers found matching your search term.
            </td>
          </tr>
        <?php endif; ?>
      </tbody>
    </table>
  </div>
</div>

<!-- ========================================== -->
<!-- CUSTOMER FLEET MODAL -->
<!-- ========================================== -->
<div class="modal fade" id="customerFleetModal" tabindex="-1" aria-labelledby="customerFleetModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered modal-lg">
    <div class="modal-content border-0 shadow">
      <div class="modal-header bg-dark text-white">
        <h5 class="modal-title fw-bold" id="customerFleetModalLabel">
          <i class="bi bi-car-front-fill text-primary me-2"></i><span id="fleetModalCustomerName"></span>'s Registered Fleet
        </h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>

      <div class="modal-body p-4">
        <div class="p-3 bg-light rounded-3 border mb-3 small d-flex flex-wrap gap-4">
          <div><strong class="text-muted">Email:</strong> <span id="fleetModalEmail" class="text-dark fw-semibold"></span></div>
          <div><strong class="text-muted">Phone:</strong> <span id="fleetModalPhone" class="text-dark fw-semibold"></span></div>
        </div>

        <h6 class="fw-bold mb-3 text-secondary text-uppercase small">Registered Vehicles</h6>
        <div id="fleetModalVehiclesList" class="d-flex flex-column gap-2">
          <!-- Dynamically populated -->
        </div>
      </div>

      <div class="modal-footer bg-light">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      </div>
    </div>
  </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function () {
  const fleetButtons = document.querySelectorAll('.view-fleet-btn');
  fleetButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      const name = this.getAttribute('data-name');
      const email = this.getAttribute('data-email');
      const phone = this.getAttribute('data-phone');
      const vehiclesJson = this.getAttribute('data-vehicles');
      const vehicles = JSON.parse(vehiclesJson || '[]');

      document.getElementById('fleetModalCustomerName').textContent = name;
      document.getElementById('fleetModalEmail').textContent = email;
      document.getElementById('fleetModalPhone').textContent = phone;

      const container = document.getElementById('fleetModalVehiclesList');
      container.innerHTML = '';

      if (vehicles.length === 0) {
        container.innerHTML = '<div class="text-muted py-3 text-center">No vehicles registered yet by this customer.</div>';
      } else {
        vehicles.forEach(v => {
          const item = document.createElement('div');
          item.className = 'p-3 border rounded-3 bg-white d-flex justify-content-between align-items-center shadow-sm';
          item.innerHTML = `
            <div>
              <div class="fw-bold text-dark fs-6">${v.brand} ${v.model}</div>
              <div class="small text-muted d-flex align-items-center gap-2 mt-1">
                <span class="badge bg-dark text-white font-monospace">${v.reg_number}</span>
                <span>Type: ${v.vehicle_type}</span>
                <span>&bull;</span>
                <span>Year: ${v.year}</span>
                <span>&bull;</span>
                <span class="badge bg-info-subtle text-info-emphasis border border-info-subtle">${v.fuel_type}</span>
              </div>
            </div>
            <a href="<?= url('admin/requests.php') ?>?search=${encodeURIComponent(v.reg_number)}" class="btn btn-sm btn-outline-primary">
              <i class="bi bi-clock-history me-1"></i> Filter Requests
            </a>
          `;
          container.appendChild(item);
        });
      }
    });
  });
});
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
