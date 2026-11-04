<?php
/**
 * Vehicle Service Management System
 * Admin Requests Management (Filter, View, Update Status, Remarks & Cost)
 */

require_once __DIR__ . '/../config/db.php';
require_once __DIR__ . '/../includes/auth_check.php';

requireAdmin();

$pdo = getDB();

// Handle Status & Remark & Cost Update
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';
    $requestId = (int)($_POST['request_id'] ?? 0);
    $status = sanitize($_POST['status'] ?? '');
    $adminRemark = sanitize($_POST['admin_remark'] ?? '');
    $costInput = trim($_POST['cost'] ?? '');
    $csrf = $_POST['csrf_token'] ?? '';

    if (!validateCsrfToken($csrf)) {
        setFlash('danger', 'Security verification failed.');
        redirect('admin/requests.php');
    }

    $validStatuses = ['Pending', 'In Progress', 'Completed', 'Cancelled'];
    if (!in_array($status, $validStatuses, true)) {
        setFlash('danger', 'Invalid status selection.');
        redirect('admin/requests.php');
    }

    // Process cost
    $cost = null;
    if ($costInput !== '') {
        $cost = (float)$costInput;
        if ($cost < 0) $cost = 0.00;
    }

    try {
        $stmt = $pdo->prepare("
            UPDATE service_requests
            SET status = ?,
                admin_remark = ?,
                cost = ?,
                updated_at = NOW()
            WHERE id = ?
        ");
        $stmt->execute([$status, $adminRemark ?: null, $cost, $requestId]);

        setFlash('success', "Service Request #$requestId updated to status '$status' with remark & billing info.");
    } catch (PDOException $e) {
        setFlash('danger', 'Error updating request: ' . $e->getMessage());
    }

    redirect('admin/requests.php');
}

// Fetch all service requests with full customer, vehicle, and service details
$stmt = $pdo->query("
    SELECT sr.*,
           u.name as customer_name, u.email as customer_email, u.phone as customer_phone, u.address as customer_address,
           v.brand, v.model, v.reg_number, v.vehicle_type, v.fuel_type, v.year,
           s.service_name, s.base_price, s.description as service_desc
    FROM service_requests sr
    JOIN users u ON sr.user_id = u.id
    JOIN vehicles v ON sr.vehicle_id = v.id
    JOIN services s ON sr.service_id = s.id
    ORDER BY sr.id DESC
");
$allRequests = $stmt->fetchAll();

// Count per status
$counts = [
    'all' => count($allRequests),
    'pending' => 0,
    'in progress' => 0,
    'completed' => 0,
    'cancelled' => 0
];
foreach ($allRequests as $r) {
    $s = strtolower($r['status']);
    if (isset($counts[$s])) {
        $counts[$s]++;
    }
}

$pageTitle = 'Manage Service Requests';
$activeNav = 'admin_requests';
$isDashboard = true;
require_once __DIR__ . '/../includes/header.php';
?>

<div class="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
  <div>
    <h2 class="h3 fw-bold mb-1"><i class="bi bi-clipboard2-check-fill text-primary me-2"></i>Service Request Queue</h2>
    <p class="text-muted small mb-0">Review service tickets, dispatch mechanics, update progress, and finalize invoices.</p>
  </div>
</div>

<!-- Filter Bar -->
<div class="card border-0 shadow-sm mb-4">
  <div class="card-body p-3">
    <div class="row g-3 align-items-center">
      <!-- Status Pills -->
      <div class="col-lg-7">
        <div class="d-flex flex-wrap gap-2">
          <button type="button" class="btn btn-sm btn-primary active" data-status-btn="all" data-target-table="adminRequestsTable">
            All <span class="badge bg-white text-dark ms-1"><?= $counts['all'] ?></span>
          </button>
          <button type="button" class="btn btn-sm btn-outline-secondary" data-status-btn="Pending" data-target-table="adminRequestsTable">
            Pending <span class="badge bg-warning text-dark ms-1"><?= $counts['pending'] ?></span>
          </button>
          <button type="button" class="btn btn-sm btn-outline-secondary" data-status-btn="In Progress" data-target-table="adminRequestsTable">
            In Progress <span class="badge bg-primary text-white ms-1"><?= $counts['in progress'] ?></span>
          </button>
          <button type="button" class="btn btn-sm btn-outline-secondary" data-status-btn="Completed" data-target-table="adminRequestsTable">
            Completed <span class="badge bg-success text-white ms-1"><?= $counts['completed'] ?></span>
          </button>
          <button type="button" class="btn btn-sm btn-outline-secondary" data-status-btn="Cancelled" data-target-table="adminRequestsTable">
            Cancelled <span class="badge bg-secondary text-white ms-1"><?= $counts['cancelled'] ?></span>
          </button>
        </div>
      </div>

      <!-- Live Search Box -->
      <div class="col-lg-5">
        <div class="input-group">
          <span class="input-group-text bg-light border-end-0"><i class="bi bi-search text-muted"></i></span>
          <input type="text" class="form-control border-start-0" data-table-search="adminRequestsTable" placeholder="Search customer, vehicle, reg #, service, ID...">
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Requests Table -->
<div class="card shadow-sm border-0">
  <div class="table-responsive">
    <table class="table table-custom align-middle mb-0" id="adminRequestsTable">
      <thead>
        <tr>
          <th>Req #</th>
          <th>Customer</th>
          <th>Vehicle</th>
          <th>Service</th>
          <th>Preferred Date</th>
          <th>Status</th>
          <th>Cost</th>
          <th>Remarks</th>
          <th class="text-end">Action</th>
        </tr>
      </thead>
      <tbody>
        <?php if (empty($allRequests)): ?>
          <tr class="no-filter">
            <td colspan="9" class="text-center py-5 text-muted">
              <i class="bi bi-inbox fs-1 text-secondary opacity-50 d-block mb-3"></i>
              No service requests found.
            </td>
          </tr>
        <?php else: ?>
          <?php foreach ($allRequests as $req): ?>
            <tr data-status="<?= escape($req['status']) ?>" id="req-row-<?= $req['id'] ?>">
              <td>
                <span class="fw-bold font-monospace text-primary">#<?= $req['id'] ?></span>
              </td>
              <td>
                <div class="fw-bold text-dark"><?= escape($req['customer_name']) ?></div>
                <div class="small text-muted"><i class="bi bi-telephone me-1"></i><?= escape($req['customer_phone']) ?></div>
                <div class="small text-secondary" style="font-size: 0.75rem;"><?= escape($req['customer_email']) ?></div>
              </td>
              <td>
                <div class="fw-semibold text-dark"><?= escape($req['brand'] . ' ' . $req['model']) ?></div>
                <div class="d-flex align-items-center gap-1 mt-1">
                  <span class="badge bg-dark text-white font-monospace" style="font-size: 0.7rem;"><?= escape($req['reg_number']) ?></span>
                  <span class="badge bg-light text-secondary border" style="font-size: 0.65rem;"><?= escape($req['fuel_type']) ?></span>
                </div>
              </td>
              <td>
                <div class="fw-semibold text-dark"><?= escape($req['service_name']) ?></div>
                <div class="small text-muted">Base: <?= formatCurrency($req['base_price']) ?></div>
              </td>
              <td>
                <div class="fw-semibold text-dark"><?= formatDate($req['preferred_date']) ?></div>
                <div class="small text-muted">Booked: <?= formatDate($req['created_at']) ?></div>
              </td>
              <td>
                <?= statusBadge($req['status']) ?>
              </td>
              <td>
                <?php if ($req['cost'] !== null): ?>
                  <span class="fw-bold text-success fs-6"><?= formatCurrency($req['cost']) ?></span>
                <?php else: ?>
                  <span class="text-muted small">Not set</span>
                <?php endif; ?>
              </td>
              <td>
                <?php if (!empty($req['admin_remark'])): ?>
                  <span class="text-truncate d-inline-block text-secondary small" style="max-width: 140px;" title="<?= escape($req['admin_remark']) ?>">
                    <?= escape($req['admin_remark']) ?>
                  </span>
                <?php else: ?>
                  <span class="text-muted small">—</span>
                <?php endif; ?>
              </td>
              <td class="text-end">
                <button type="button" class="btn btn-sm btn-primary update-status-btn"
                        data-bs-toggle="modal"
                        data-bs-target="#updateStatusModal"
                        data-id="<?= $req['id'] ?>"
                        data-customer="<?= escape($req['customer_name'] . ' (' . $req['customer_phone'] . ')') ?>"
                        data-vehicle="<?= escape($req['brand'] . ' ' . $req['model'] . ' - ' . $req['reg_number']) ?>"
                        data-service="<?= escape($req['service_name']) ?>"
                        data-baseprice="<?= $req['base_price'] ?>"
                        data-desc="<?= escape($req['description'] ?: 'None') ?>"
                        data-status="<?= escape($req['status']) ?>"
                        data-remark="<?= escape($req['admin_remark'] ?? '') ?>"
                        data-cost="<?= $req['cost'] !== null ? escape($req['cost']) : '' ?>"
                        title="Update Request Status">
                  <i class="bi bi-gear-fill me-1"></i> Update
                </button>
              </td>
            </tr>
          <?php endforeach; ?>
          <tr class="empty-filter-row" style="display: none;">
            <td colspan="9" class="text-center py-4 text-muted">
              <i class="bi bi-filter-circle me-1"></i> No requests match the selected filter.
            </td>
          </tr>
        <?php endif; ?>
      </tbody>
    </table>
  </div>
</div>

<!-- ========================================== -->
<!-- UPDATE STATUS MODAL -->
<!-- ========================================== -->
<div class="modal fade" id="updateStatusModal" tabindex="-1" aria-labelledby="updateStatusModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content border-0 shadow">
      <div class="modal-header bg-dark text-white">
        <h5 class="modal-title fw-bold" id="updateStatusModalLabel">
          <i class="bi bi-wrench-adjustable-circle text-primary me-2"></i>Update Request <span id="modalUpdateIdBadge" class="badge bg-primary"></span>
        </h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>

      <form action="<?= url('admin/requests.php') ?>" method="POST">
        <?php csrfField(); ?>
        <input type="hidden" name="action" value="update_status">
        <input type="hidden" name="request_id" id="modal_request_id" value="">

        <div class="modal-body p-4">
          <!-- Request Summary Strip -->
          <div class="p-3 bg-light rounded-3 border mb-3 small">
            <div><strong>Customer:</strong> <span id="modalCustomerText"></span></div>
            <div><strong>Vehicle:</strong> <span id="modalVehicleText"></span></div>
            <div><strong>Service:</strong> <span id="modalServiceText"></span></div>
            <div class="mt-1 text-muted"><strong>Customer Notes:</strong> <span id="modalNotesText" class="fst-italic"></span></div>
          </div>

          <!-- Status Dropdown -->
          <div class="mb-3">
            <label for="modal_status" class="form-label fw-bold">Service Status <span class="text-danger">*</span></label>
            <select class="form-select" id="modal_status" name="status" required>
              <option value="Pending">Pending (Awaiting Bay / Inspection)</option>
              <option value="In Progress">In Progress (Under Active Service)</option>
              <option value="Completed">Completed (Ready for Delivery)</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>

          <!-- Cost Input -->
          <div class="mb-3">
            <label for="modal_cost" class="form-label fw-bold">Final Cost / Bill Amount ($)</label>
            <div class="input-group">
              <span class="input-group-text bg-light">$</span>
              <input type="number" step="0.01" min="0" class="form-control" id="modal_cost" name="cost" placeholder="e.g. 120.00">
            </div>
            <div class="form-text">Enter base or adjusted service charges after parts inspection.</div>
          </div>

          <!-- Admin Remark -->
          <div class="mb-2">
            <label for="modal_remark" class="form-label fw-bold">Admin Remark / Technician Note</label>
            <textarea class="form-control" id="modal_remark" name="admin_remark" rows="3" placeholder="Enter workshop notes, parts replaced, diagnostic findings, or reason for status update..."></textarea>
            <div class="form-text">Customer will be able to see these remarks in their history details.</div>
          </div>
        </div>

        <div class="modal-footer bg-light">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          <button type="submit" class="btn btn-primary">
            <i class="bi bi-check2-circle me-1"></i> Save Changes
          </button>
        </div>
      </form>
    </div>
  </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function () {
  const updateButtons = document.querySelectorAll('.update-status-btn');
  updateButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      const id = this.getAttribute('data-id');
      const customer = this.getAttribute('data-customer');
      const vehicle = this.getAttribute('data-vehicle');
      const service = this.getAttribute('data-service');
      const desc = this.getAttribute('data-desc');
      const status = this.getAttribute('data-status');
      const remark = this.getAttribute('data-remark');
      const cost = this.getAttribute('data-cost');

      document.getElementById('modalUpdateIdBadge').textContent = '#' + id;
      document.getElementById('modal_request_id').value = id;
      document.getElementById('modalCustomerText').textContent = customer;
      document.getElementById('modalVehicleText').textContent = vehicle;
      document.getElementById('modalServiceText').textContent = service;
      document.getElementById('modalNotesText').textContent = desc;

      document.getElementById('modal_status').value = status;
      document.getElementById('modal_remark').value = remark;
      document.getElementById('modal_cost').value = cost;
    });
  });

  // Check if req_id is in URL, auto trigger that update modal
  const urlParams = new URLSearchParams(window.location.search);
  const targetReqId = urlParams.get('req_id');
  if (targetReqId) {
    const targetRow = document.getElementById('req-row-' + targetReqId);
    if (targetRow) {
      targetRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
      const targetBtn = targetRow.querySelector('.update-status-btn');
      if (targetBtn) {
        targetBtn.click();
      }
    }
  }
});
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
