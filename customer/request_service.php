<?php
/**
 * Vehicle Service Management System
 * Customer Service Booking Request
 */

require_once __DIR__ . '/../config/db.php';
require_once __DIR__ . '/../includes/auth_check.php';

requireCustomer();

$userId = $_SESSION['user_id'];
$pdo = getDB();
$errors = [];

// Pre-selected vehicle ID from query param
$selectedVehicleId = (int)($_GET['vehicle_id'] ?? 0);

// Fetch all vehicles belonging to the customer
$stmt = $pdo->prepare("SELECT * FROM vehicles WHERE user_id = ? ORDER BY id DESC");
$stmt->execute([$userId]);
$vehicles = $stmt->fetchAll();

// Fetch all available services
$stmt = $pdo->query("SELECT * FROM services ORDER BY base_price ASC");
$services = $stmt->fetchAll();

// Handle Form Submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $vehicleId = (int)($_POST['vehicle_id'] ?? 0);
    $serviceId = (int)($_POST['service_id'] ?? 0);
    $preferredDate = sanitize($_POST['preferred_date'] ?? '');
    $description = sanitize($_POST['description'] ?? '');
    $csrf = $_POST['csrf_token'] ?? '';

    if (!validateCsrfToken($csrf)) {
        $errors[] = 'Security verification failed. Please try again.';
    }

    // Validate vehicle ownership
    $stmt = $pdo->prepare("SELECT id, brand, model, reg_number FROM vehicles WHERE id = ? AND user_id = ?");
    $stmt->execute([$vehicleId, $userId]);
    $veh = $stmt->fetch();
    if (!$veh) {
        $errors[] = 'Please select a valid vehicle from your registered list.';
    }

    // Validate service exists
    $stmt = $pdo->prepare("SELECT id, service_name, base_price FROM services WHERE id = ?");
    $stmt->execute([$serviceId]);
    $srv = $stmt->fetch();
    if (!$srv) {
        $errors[] = 'Please select a valid service package.';
    }

    // Validate preferred date (cannot be before today)
    $today = date('Y-m-d');
    if (empty($preferredDate)) {
        $errors[] = 'Please select your preferred service date.';
    } elseif ($preferredDate < $today) {
        $errors[] = 'Preferred appointment date cannot be in the past.';
    }

    if (empty($errors)) {
        try {
            $stmt = $pdo->prepare("
                INSERT INTO service_requests (user_id, vehicle_id, service_id, preferred_date, description, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'Pending', NOW(), NOW())
            ");
            $stmt->execute([$userId, $vehicleId, $serviceId, $preferredDate, $description]);
            $requestId = $pdo->lastInsertId();

            setFlash('success', "Service request #$requestId for {$veh['brand']} {$veh['model']} submitted successfully! Our service advisors will review it shortly.");
            redirect('customer/history.php');
        } catch (PDOException $e) {
            $errors[] = 'Database error creating service booking: ' . $e->getMessage();
        }
    }
}

$pageTitle = 'Book Service';
$activeNav = 'request_service';
$isDashboard = true;
require_once __DIR__ . '/../includes/header.php';
?>

<div class="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
  <div>
    <h2 class="h3 fw-bold mb-1"><i class="bi bi-calendar-plus-fill text-primary me-2"></i>Book a Service Appointment</h2>
    <p class="text-muted small mb-0">Select your vehicle, choose maintenance or repairs, and schedule your preferred service date.</p>
  </div>
  <a href="<?= url('customer/history.php') ?>" class="btn btn-outline-secondary btn-sm">
    <i class="bi bi-clock-history me-1"></i> View History
  </a>
</div>

<?php if (empty($vehicles)): ?>
  <!-- Alert prompt if customer has no vehicles registered yet -->
  <div class="card border-0 shadow-sm rounded-4 p-5 text-center">
    <div class="mb-3">
      <span class="p-3 rounded-circle bg-warning-subtle text-warning d-inline-flex align-items-center justify-content-center">
        <i class="bi bi-exclamation-triangle-fill fs-2"></i>
      </span>
    </div>
    <h4 class="fw-bold text-dark">No Vehicles in Your Garage</h4>
    <p class="text-muted mx-auto mb-4" style="max-width: 500px;">
      Before scheduling an appointment or repair, please add at least one vehicle to your account.
    </p>
    <div>
      <a href="<?= url('customer/vehicles.php') ?>" class="btn btn-primary px-4 py-2">
        <i class="bi bi-plus-circle me-1"></i> Add Vehicle Now
      </a>
    </div>
  </div>
<?php else: ?>

  <div class="row g-4">
    <!-- Booking Form -->
    <div class="col-lg-7">
      <div class="card border-0 shadow-sm rounded-4">
        <div class="card-header bg-white py-3">
          <h5 class="fw-bold mb-0 text-dark">Service Appointment Details</h5>
        </div>

        <div class="card-body p-4">
          <?php if (!empty($errors)): ?>
            <div class="alert alert-danger shadow-sm">
              <ul class="mb-0 ps-3">
                <?php foreach ($errors as $err): ?>
                  <li><?= escape($err) ?></li>
                <?php endforeach; ?>
              </ul>
            </div>
          <?php endif; ?>

          <form action="<?= url('customer/request_service.php') ?>" method="POST" class="needs-validation" novalidate>
            <?php csrfField(); ?>

            <!-- Select Vehicle -->
            <div class="mb-3">
              <label for="vehicle_id" class="form-label">Select Vehicle <span class="text-danger">*</span></label>
              <select class="form-select form-select-lg fs-6" id="vehicle_id" name="vehicle_id" required>
                <option value="">-- Choose from your registered vehicles --</option>
                <?php foreach ($vehicles as $v): ?>
                  <option value="<?= $v['id'] ?>" <?= ($selectedVehicleId === (int)$v['id']) ? 'selected' : '' ?>>
                    <?= escape($v['brand'] . ' ' . $v['model']) ?> &bull; <?= escape($v['reg_number']) ?> (<?= escape($v['vehicle_type']) ?> - <?= escape($v['fuel_type']) ?>)
                  </option>
                <?php endforeach; ?>
              </select>
              <div class="invalid-feedback">Please choose a vehicle.</div>
              <div class="form-text">
                Need to service another car? <a href="<?= url('customer/vehicles.php') ?>" class="text-primary text-decoration-none">Add a new vehicle</a>.
              </div>
            </div>

            <!-- Select Service -->
            <div class="mb-3">
              <label for="service_id" class="form-label">Service Required <span class="text-danger">*</span></label>
              <select class="form-select form-select-lg fs-6" id="service_id" name="service_id" required>
                <option value="">-- Select Service Type --</option>
                <?php foreach ($services as $s): ?>
                  <option value="<?= $s['id'] ?>" data-price="<?= $s['base_price'] ?>" data-desc="<?= escape($s['description']) ?>">
                    <?= escape($s['service_name']) ?> (Base <?= formatCurrency($s['base_price']) ?>)
                  </option>
                <?php endforeach; ?>
              </select>
              <div class="invalid-feedback">Please select a service type.</div>
            </div>

            <!-- Preferred Date -->
            <div class="mb-3">
              <label for="preferred_date" class="form-label">Preferred Service Date <span class="text-danger">*</span></label>
              <input type="date" class="form-control" id="preferred_date" name="preferred_date" min="<?= date('Y-m-d') ?>" value="<?= date('Y-m-d') ?>" required>
              <div class="invalid-feedback">Please choose a valid appointment date (today or future).</div>
            </div>

            <!-- Description / Issues -->
            <div class="mb-4">
              <label for="description" class="form-label">Description of Issues or Special Instructions</label>
              <textarea class="form-control" id="description" name="description" rows="3" placeholder="Describe any problems, noises, specific requests or instructions for our mechanics..."></textarea>
              <div class="form-text">Include any symptoms like vibration, dashboard warning lights, or squeaking.</div>
            </div>

            <button type="submit" class="btn btn-primary w-100 py-2 fs-6 shadow-sm">
              <i class="bi bi-send-check me-1"></i> Submit Service Request
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- Live Preview & Service Information Box -->
    <div class="col-lg-5">
      <!-- Live Estimate Box -->
      <div class="card border-0 shadow-sm rounded-4 mb-4">
        <div class="card-header bg-white py-3">
          <h5 class="fw-bold mb-0"><i class="bi bi-tag-fill text-primary me-2"></i>Estimated Estimate Preview</h5>
        </div>
        <div class="card-body p-4">
          <div id="servicePriceAlert" class="d-none">
            <div class="p-3 bg-light rounded-3 border mb-3">
              <div class="text-muted small">Estimated Service Base Cost</div>
              <div class="display-6 fw-bold text-primary mt-1" id="servicePriceDisplay">$0.00</div>
              <p class="text-secondary small mt-2 mb-0" id="serviceDescDisplay"></p>
            </div>
            <div class="alert alert-info py-2 small mb-0">
              <i class="bi bi-info-circle me-1"></i> Final billing cost will be reviewed and confirmed by service advisor upon physical inspection.
            </div>
          </div>
          <div id="noSelectionMsg" class="text-center py-4 text-muted">
            <i class="bi bi-receipt-cutoff fs-2 opacity-50 d-block mb-2"></i>
            Select a service package from the dropdown to see instant pricing details.
          </div>
        </div>
      </div>

      <!-- Service Guarantees -->
      <div class="card border-0 shadow-sm rounded-4 p-4 bg-dark text-white">
        <h6 class="fw-bold mb-3 text-white"><i class="bi bi-shield-check text-primary me-2"></i>VSM Service Promise</h6>
        <ul class="list-unstyled mb-0 d-flex flex-column gap-2 small text-white-50">
          <li><i class="bi bi-check2 text-success me-2"></i>OEM Genuine replacement parts & manufacturer-approved lubricants</li>
          <li><i class="bi bi-check2 text-success me-2"></i>Multi-point computerized safety inspection with every booking</li>
          <li><i class="bi bi-check2 text-success me-2"></i>Real-time status updates through your customer portal</li>
          <li><i class="bi bi-check2 text-success me-2"></i>Instant cancellation available while request is Pending</li>
        </ul>
      </div>
    </div>
  </div>

  <script>
  // Hide placeholder when service is picked
  document.addEventListener('DOMContentLoaded', function () {
    const srvSelect = document.getElementById('service_id');
    const noMsg = document.getElementById('noSelectionMsg');
    if (srvSelect && noMsg) {
      srvSelect.addEventListener('change', function () {
        if (this.value) {
          noMsg.classList.add('d-none');
        } else {
          noMsg.classList.remove('d-none');
        }
      });
    }
  });
  </script>

<?php endif; ?>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
