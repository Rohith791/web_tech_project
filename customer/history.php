<?php
/**
 * Vehicle Service Management System
 * Customer Service History & Cancellation
 */

require_once __DIR__ . '/../config/db.php';
require_once __DIR__ . '/../includes/auth_check.php';

requireCustomer();

$userId = $_SESSION['user_id'];
$pdo = getDB();

// Handle Cancellation of a Pending request
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';
    $requestId = (int)($_POST['request_id'] ?? 0);
    $csrf = $_POST['csrf_token'] ?? '';

    if (!validateCsrfToken($csrf)) {
        setFlash('danger', 'Security token invalid. Please try again.');
        redirect('customer/history.php');
    }

    if ($action === 'cancel') {
        // Verify ownership and Pending status
        $stmt = $pdo->prepare("SELECT id, status FROM service_requests WHERE id = ? AND user_id = ?");
        $stmt->execute([$requestId, $userId]);
        $req = $stmt->fetch();

        if (!$req) {
            setFlash('danger', 'Service request not found or unauthorized.');
        } elseif ($req['status'] !== 'Pending') {
            setFlash('warning', "Cannot cancel request #$requestId because its status is already '{$req['status']}'. Only 'Pending' requests can be cancelled.");
        } else {
            $stmt = $pdo->prepare("
                UPDATE service_requests 
                SET status = 'Cancelled', 
                    admin_remark = COALESCE(CONCAT(admin_remark, ' | Cancelled by customer on request'), 'Cancelled by customer on request.'),
                    cost = 0.00,
                    updated_at = NOW() 
                WHERE id = ? AND user_id = ?
            ");
            $stmt->execute([$requestId, $userId]);
            setFlash('success', "Service request #$requestId has been cancelled successfully.");
        }
        redirect('customer/history.php');
    }
}

// Fetch all requests for this customer
$stmt = $pdo->prepare("
    SELECT sr.*, 
           v.brand, v.model, v.reg_number, v.vehicle_type, v.fuel_type, v.year,
           s.service_name, s.base_price, s.description as service_desc
    FROM service_requests sr
    JOIN vehicles v ON sr.vehicle_id = v.id
    JOIN services s ON sr.service_id = s.id
    WHERE sr.user_id = ?
    ORDER BY sr.id DESC
");
$stmt->execute([$userId]);
$requests = $stmt->fetchAll();

// Calculate counts per status
$counts = [
    'all' => count($requests),
    'pending' => 0,
    'in progress' => 0,
    'completed' => 0,
    'cancelled' => 0
];
foreach ($requests as $r) {
    $s = strtolower($r['status']);
    if (isset($counts[$s])) {
        $counts[$s]++;
    }
}

$pageTitle = 'Service History';
$activeNav = 'history';
$isDashboard = true;
require_once __DIR__ . '/../includes/header.php';
?>

<div class="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
  <div>
    <h2 class="h3 fw-bold mb-1"><i class="bi bi-clock-history text-primary me-2"></i>Service Request History</h2>
    <p class="text-muted small mb-0">Track maintenance records, view workshop remarks, and manage pending appointments.</p>
  </div>
  <a href="<?= url('customer/request_service.php') ?>" class="btn btn-primary shadow-sm">
    <i class="bi bi-calendar-plus me-1"></i> Book New Service
  </a>
</div>

<!-- Status Filter Tabs & Search Bar -->
<div class="card border-0 shadow-sm mb-4">
  <div class="card-body p-3">
    <div class="row g-3 align-items-center">
      <!-- Status Pills -->
      <div class="col-lg-7">
        <div class="d-flex flex-wrap gap-2">
          <button type="button" class="btn btn-sm btn-primary active" data-status-btn="all" data-target-table="historyTable">
            All Records <span class="badge bg-white text-dark ms-1"><?= $counts['all'] ?></span>
          </button>
          <button type="button" class="btn btn-sm btn-outline-secondary" data-status-btn="Pending" data-target-table="historyTable">
            Pending <span class="badge bg-warning text-dark ms-1"><?= $counts['pending'] ?></span>
          </button>
          <button type="button" class="btn btn-sm btn-outline-secondary" data-status-btn="In Progress" data-target-table="historyTable">
            In Progress <span class="badge bg-primary text-white ms-1"><?= $counts['in progress'] ?></span>
          </button>
          <button type="button" class="btn btn-sm btn-outline-secondary" data-status-btn="Completed" data-target-table="historyTable">
            Completed <span class="badge bg-success text-white ms-1"><?= $counts['completed'] ?></span>
          </button>
          <button type="button" class="btn btn-sm btn-outline-secondary" data-status-btn="Cancelled" data-target-table="historyTable">
            Cancelled <span class="badge bg-secondary text-white ms-1"><?= $counts['cancelled'] ?></span>
          </button>
        </div>
      </div>

      <!-- Live Search -->
      <div class="col-lg-5">
        <div class="input-group">
          <span class="input-group-text bg-light border-end-0"><i class="bi bi-search text-muted"></i></span>
          <input type="text" class="form-control border-start-0" data-table-search="historyTable" placeholder="Search vehicle, reg #, service...">
        </div>
      </div>
    </div>
  </div>
</div>

<!-- History Table -->
<div class="card shadow-sm border-0">
  <div class="table-responsive">
    <table class="table table-custom align-middle mb-0" id="historyTable">
      <thead>
        <tr>
          <th>Req #</th>
          <th>Vehicle</th>
          <th>Service Package</th>
          <th>Scheduled Date</th>
          <th>Status</th>
          <th>Total Cost</th>
          <th>Booked On</th>
          <th class="text-end">Actions</th>
        </tr>
      </thead>
      <tbody>
        <?php if (empty($requests)): ?>
          <tr class="no-filter">
            <td colspan="8" class="text-center py-5 text-muted">
              <i class="bi bi-clipboard-x fs-1 text-secondary opacity-50 d-block mb-3"></i>
              <h5 class="fw-bold text-dark">No Service Records Found</h5>
              <p class="small text-muted mb-3">You haven't booked any service requests yet.</p>
              <a href="<?= url('customer/request_service.php') ?>" class="btn btn-primary btn-sm">
                <i class="bi bi-calendar-plus me-1"></i> Book Service Now
              </a>
            </td>
          </tr>
        <?php else: ?>
          <?php foreach ($requests as $r): ?>
            <tr data-status="<?= escape($r['status']) ?>">
              <td>
                <span class="fw-bold font-monospace text-primary">#<?= $r['id'] ?></span>
              </td>
              <td>
                <div class="fw-bold text-dark"><?= escape($r['brand'] . ' ' . $r['model']) ?></div>
                <div class="small text-muted d-flex align-items-center gap-1">
                  <span class="badge bg-light text-dark border"><?= escape($r['reg_number']) ?></span>
                  <span>&bull;</span>
                  <span><?= escape($r['fuel_type']) ?></span>
                </div>
              </td>
              <td>
                <div class="fw-semibold text-dark"><?= escape($r['service_name']) ?></div>
              </td>
              <td>
                <div class="fw-semibold"><?= formatDate($r['preferred_date']) ?></div>
              </td>
              <td>
                <?= statusBadge($r['status']) ?>
              </td>
              <td class="fw-bold text-dark">
                <?php if ($r['cost'] !== null): ?>
                  <?= formatCurrency($r['cost']) ?>
                <?php else: ?>
                  <span class="text-muted small">Est. <?= formatCurrency($r['base_price']) ?></span>
                <?php endif; ?>
              </td>
              <td class="text-muted small">
                <?= formatDate($r['created_at']) ?>
              </td>
              <td class="text-end">
                <div class="d-inline-flex gap-1">
                  <!-- View Details Modal Trigger -->
                  <button type="button" class="btn btn-sm btn-outline-info view-req-btn"
                          data-bs-toggle="modal"
                          data-bs-target="#viewDetailsModal"
                          data-id="<?= $r['id'] ?>"
                          data-vehicle="<?= escape($r['brand'] . ' ' . $r['model'] . ' (' . $r['reg_number'] . ')') ?>"
                          data-type="<?= escape($r['vehicle_type']) ?> - <?= escape($r['fuel_type']) ?> (<?= escape($r['year']) ?>)"
                          data-service="<?= escape($r['service_name']) ?>"
                          data-date="<?= formatDate($r['preferred_date']) ?>"
                          data-desc="<?= escape($r['description'] ?: 'No additional notes provided.') ?>"
                          data-status="<?= escape($r['status']) ?>"
                          data-remark="<?= escape($r['admin_remark'] ?: 'No remarks posted yet.') ?>"
                          data-cost="<?= $r['cost'] !== null ? formatCurrency($r['cost']) : 'Pending inspection (Est. ' . formatCurrency($r['base_price']) . ')' ?>"
                          data-created="<?= formatDate($r['created_at']) ?>"
                          data-updated="<?= formatDate($r['updated_at']) ?>"
                          title="View Full Details">
                    <i class="bi bi-eye"></i> Details
                  </button>

                  <!-- Cancel Button (Only if Pending) -->
                  <?php if ($r['status'] === 'Pending'): ?>
                    <form action="<?= url('customer/history.php') ?>" method="POST" class="d-inline">
                      <?php csrfField(); ?>
                      <input type="hidden" name="action" value="cancel">
                      <input type="hidden" name="request_id" value="<?= $r['id'] ?>">
                      <button type="button" class="btn btn-sm btn-outline-danger"
                              data-confirm-action="cancel"
                              data-item-title="#<?= $r['id'] ?> (<?= escape($r['brand'] . ' ' . $r['model']) ?> - <?= escape($r['service_name']) ?>)"
                              title="Cancel Request">
                        <i class="bi bi-x-circle"></i> Cancel
                      </button>
                    </form>
                  <?php endif; ?>
                </div>
              </td>
            </tr>
          <?php endforeach; ?>
          <tr class="empty-filter-row" style="display: none;">
            <td colspan="8" class="text-center py-4 text-muted">
              <i class="bi bi-filter-circle me-1"></i> No service records match the selected filter or search term.
            </td>
          </tr>
        <?php endif; ?>
      </tbody>
    </table>
  </div>
</div>

<!-- ========================================== -->
<!-- VIEW DETAILS MODAL -->
<!-- ========================================== -->
<div class="modal fade" id="viewDetailsModal" tabindex="-1" aria-labelledby="viewDetailsModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered modal-lg">
    <div class="modal-content border-0 shadow">
      <div class="modal-header bg-dark text-white">
        <h5 class="modal-title fw-bold" id="viewDetailsModalLabel">
          <i class="bi bi-file-earmark-text text-primary me-2"></i>Service Request Details <span id="modalReqIdBadge" class="badge bg-primary ms-1"></span>
        </h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>

      <div class="modal-body p-4">
        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <div class="p-3 bg-light rounded-3 border">
              <div class="text-muted small text-uppercase fw-bold">Vehicle</div>
              <div class="fw-bold fs-6 text-dark mt-1" id="modalVehicle"></div>
              <div class="small text-secondary" id="modalVehicleType"></div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="p-3 bg-light rounded-3 border">
              <div class="text-muted small text-uppercase fw-bold">Service Package</div>
              <div class="fw-bold fs-6 text-dark mt-1" id="modalService"></div>
              <div class="small text-secondary">Scheduled for: <span id="modalDate" class="fw-semibold"></span></div>
            </div>
          </div>
        </div>

        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <div class="p-3 bg-light rounded-3 border">
              <div class="text-muted small text-uppercase fw-bold">Current Status</div>
              <div class="mt-1" id="modalStatusBadge"></div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="p-3 bg-light rounded-3 border">
              <div class="text-muted small text-uppercase fw-bold">Total Service Cost</div>
              <div class="fw-bold fs-5 text-primary mt-1" id="modalCost"></div>
            </div>
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label fw-bold text-dark small text-uppercase">Customer Problem Description / Notes</label>
          <div class="p-3 bg-light rounded-3 border text-secondary" id="modalDesc"></div>
        </div>

        <div class="mb-3">
          <label class="form-label fw-bold text-dark small text-uppercase">Workshop Admin Remarks & Technician Notes</label>
          <div class="p-3 bg-white rounded-3 border border-primary-subtle text-dark" id="modalRemark" style="background-color: #f8fafc !important;"></div>
        </div>

        <div class="d-flex justify-content-between text-muted small pt-2 border-top">
          <span>Created on: <strong id="modalCreated"></strong></span>
          <span>Last Updated: <strong id="modalUpdated"></strong></span>
        </div>
      </div>

      <div class="modal-footer bg-light">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      </div>
    </div>
  </div>
</div>

<script>
// Populate Details Modal on click
document.addEventListener('DOMContentLoaded', function () {
  const viewButtons = document.querySelectorAll('.view-req-btn');
  viewButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      const id = this.getAttribute('data-id');
      const vehicle = this.getAttribute('data-vehicle');
      const type = this.getAttribute('data-type');
      const service = this.getAttribute('data-service');
      const date = this.getAttribute('data-date');
      const desc = this.getAttribute('data-desc');
      const status = this.getAttribute('data-status');
      const remark = this.getAttribute('data-remark');
      const cost = this.getAttribute('data-cost');
      const created = this.getAttribute('data-created');
      const updated = this.getAttribute('data-updated');

      document.getElementById('modalReqIdBadge').textContent = '#' + id;
      document.getElementById('modalVehicle').textContent = vehicle;
      document.getElementById('modalVehicleType').textContent = type;
      document.getElementById('modalService').textContent = service;
      document.getElementById('modalDate').textContent = date;
      document.getElementById('modalDesc').textContent = desc;
      document.getElementById('modalRemark').textContent = remark;
      document.getElementById('modalCost').textContent = cost;
      document.getElementById('modalCreated').textContent = created;
      document.getElementById('modalUpdated').textContent = updated;

      // Status badge styling in modal
      let badgeHtml = '';
      if (status === 'Pending') {
        badgeHtml = '<span class="badge bg-warning text-dark fs-6"><i class="bi bi-clock-history me-1"></i>Pending</span>';
      } else if (status === 'In Progress') {
        badgeHtml = '<span class="badge bg-primary fs-6"><i class="bi bi-gear-wide-connected me-1"></i>In Progress</span>';
      } else if (status === 'Completed') {
        badgeHtml = '<span class="badge bg-success fs-6"><i class="bi bi-check-circle-fill me-1"></i>Completed</span>';
      } else {
        badgeHtml = '<span class="badge bg-danger fs-6"><i class="bi bi-x-circle-fill me-1"></i>Cancelled</span>';
      }
      document.getElementById('modalStatusBadge').innerHTML = badgeHtml;
    });
  });
});
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
