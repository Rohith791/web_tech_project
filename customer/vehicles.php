<?php
/**
 * Vehicle Service Management System
 * Customer Vehicles Management (Add, View, Edit, Delete)
 */

require_once __DIR__ . '/../config/db.php';
require_once __DIR__ . '/../includes/auth_check.php';

requireCustomer();

$userId = $_SESSION['user_id'];
$pdo = getDB();
$errors = [];

// Handle POST actions: add, edit, delete
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';
    $csrf = $_POST['csrf_token'] ?? '';

    if (!validateCsrfToken($csrf)) {
        setFlash('danger', 'Security token invalid or expired. Please try again.');
        redirect('customer/vehicles.php');
    }

    // 1. ADD VEHICLE
    if ($action === 'add') {
        $vehicleType = sanitize($_POST['vehicle_type'] ?? '');
        $brand = sanitize($_POST['brand'] ?? '');
        $model = sanitize($_POST['model'] ?? '');
        $regNumber = strtoupper(sanitize($_POST['reg_number'] ?? ''));
        $year = (int)($_POST['year'] ?? 0);
        $fuelType = sanitize($_POST['fuel_type'] ?? '');

        $currentYear = (int)date('Y');
        if (empty($vehicleType) || empty($brand) || empty($model) || empty($regNumber) || empty($fuelType)) {
            setFlash('danger', 'All vehicle fields are required.');
            redirect('customer/vehicles.php');
        } elseif ($year < 1980 || $year > $currentYear + 1) {
            setFlash('danger', "Manufacturing year must be between 1980 and " . ($currentYear + 1) . ".");
            redirect('customer/vehicles.php');
        } else {
            // Check for duplicate registration number
            $stmt = $pdo->prepare("SELECT id FROM vehicles WHERE reg_number = ?");
            $stmt->execute([$regNumber]);
            if ($stmt->fetch()) {
                setFlash('danger', "A vehicle with registration number '$regNumber' already exists.");
                redirect('customer/vehicles.php');
            } else {
                $stmt = $pdo->prepare("
                    INSERT INTO vehicles (user_id, vehicle_type, brand, model, reg_number, year, fuel_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, NOW())
                ");
                $stmt->execute([$userId, $vehicleType, $brand, $model, $regNumber, $year, $fuelType]);
                setFlash('success', "Vehicle $brand $model ($regNumber) added successfully!");
                redirect('customer/vehicles.php');
            }
        }
    }

    // 2. EDIT VEHICLE
    elseif ($action === 'edit') {
        $vehicleId = (int)($_POST['vehicle_id'] ?? 0);
        $vehicleType = sanitize($_POST['vehicle_type'] ?? '');
        $brand = sanitize($_POST['brand'] ?? '');
        $model = sanitize($_POST['model'] ?? '');
        $regNumber = strtoupper(sanitize($_POST['reg_number'] ?? ''));
        $year = (int)($_POST['year'] ?? 0);
        $fuelType = sanitize($_POST['fuel_type'] ?? '');

        // Verify vehicle ownership
        $stmt = $pdo->prepare("SELECT id FROM vehicles WHERE id = ? AND user_id = ?");
        $stmt->execute([$vehicleId, $userId]);
        if (!$stmt->fetch()) {
            setFlash('danger', 'Unauthorized or vehicle not found.');
            redirect('customer/vehicles.php');
        }

        $currentYear = (int)date('Y');
        if (empty($vehicleType) || empty($brand) || empty($model) || empty($regNumber) || empty($fuelType)) {
            setFlash('danger', 'All vehicle fields are required.');
            redirect('customer/vehicles.php');
        } elseif ($year < 1980 || $year > $currentYear + 1) {
            setFlash('danger', "Manufacturing year must be between 1980 and " . ($currentYear + 1) . ".");
            redirect('customer/vehicles.php');
        } else {
            // Check if reg_number conflicts with another vehicle
            $stmt = $pdo->prepare("SELECT id FROM vehicles WHERE reg_number = ? AND id != ?");
            $stmt->execute([$regNumber, $vehicleId]);
            if ($stmt->fetch()) {
                setFlash('danger', "Registration number '$regNumber' is already in use by another vehicle.");
                redirect('customer/vehicles.php');
            } else {
                $stmt = $pdo->prepare("
                    UPDATE vehicles 
                    SET vehicle_type = ?, brand = ?, model = ?, reg_number = ?, year = ?, fuel_type = ?
                    WHERE id = ? AND user_id = ?
                ");
                $stmt->execute([$vehicleType, $brand, $model, $regNumber, $year, $fuelType, $vehicleId, $userId]);
                setFlash('success', "Vehicle $brand $model ($regNumber) updated successfully!");
                redirect('customer/vehicles.php');
            }
        }
    }

    // 3. DELETE VEHICLE
    elseif ($action === 'delete') {
        $vehicleId = (int)($_POST['vehicle_id'] ?? 0);

        // Verify vehicle ownership
        $stmt = $pdo->prepare("SELECT brand, model, reg_number FROM vehicles WHERE id = ? AND user_id = ?");
        $stmt->execute([$vehicleId, $userId]);
        $veh = $stmt->fetch();

        if ($veh) {
            $stmt = $pdo->prepare("DELETE FROM vehicles WHERE id = ? AND user_id = ?");
            $stmt->execute([$vehicleId, $userId]);
            setFlash('success', "Vehicle {$veh['brand']} {$veh['model']} ({$veh['reg_number']}) was removed.");
        } else {
            setFlash('danger', 'Vehicle not found or already deleted.');
        }
        redirect('customer/vehicles.php');
    }
}

// Fetch user's vehicles with service request counts
$stmt = $pdo->prepare("
    SELECT v.*, COUNT(sr.id) as service_count
    FROM vehicles v
    LEFT JOIN service_requests sr ON v.id = sr.vehicle_id
    WHERE v.user_id = ?
    GROUP BY v.id
    ORDER BY v.id DESC
");
$stmt->execute([$userId]);
$vehicles = $stmt->fetchAll();

$pageTitle = 'My Vehicles';
$activeNav = 'vehicles';
$isDashboard = true;
require_once __DIR__ . '/../includes/header.php';
?>

<div class="d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3">
  <div>
    <h2 class="h3 fw-bold mb-1"><i class="bi bi-car-front-fill text-primary me-2"></i>My Registered Vehicles</h2>
    <p class="text-muted small mb-0">View, add, edit, or remove vehicles registered under your account.</p>
  </div>
  <button type="button" class="btn btn-primary shadow-sm" data-bs-toggle="modal" data-bs-target="#addVehicleModal">
    <i class="bi bi-plus-lg me-1"></i> Register New Vehicle
  </button>
</div>

<!-- Search & Counter Bar -->
<div class="card border-0 shadow-sm mb-4">
  <div class="card-body p-3">
    <div class="row g-3 align-items-center">
      <div class="col-md-6 col-lg-8">
        <div class="input-group">
          <span class="input-group-text bg-light border-end-0"><i class="bi bi-search text-muted"></i></span>
          <input type="text" class="form-control border-start-0" data-table-search="vehiclesTable" placeholder="Search by brand, model, reg number, fuel type...">
        </div>
      </div>
      <div class="col-md-6 col-lg-4 text-md-end text-muted small">
        Total Fleet: <span class="fw-bold text-dark fs-6"><?= count($vehicles) ?></span> vehicles
      </div>
    </div>
  </div>
</div>

<!-- Vehicles Table / List -->
<div class="card shadow-sm border-0">
  <div class="table-responsive">
    <table class="table table-custom align-middle mb-0" id="vehiclesTable">
      <thead>
        <tr>
          <th>Vehicle Details</th>
          <th>Type</th>
          <th>Reg. Number</th>
          <th>Year</th>
          <th>Fuel</th>
          <th>Services Booked</th>
          <th class="text-end">Actions</th>
        </tr>
      </thead>
      <tbody>
        <?php if (empty($vehicles)): ?>
          <tr class="no-filter">
            <td colspan="7" class="text-center py-5 text-muted">
              <i class="bi bi-car-front fs-1 text-secondary opacity-50 d-block mb-3"></i>
              <h5 class="fw-bold text-dark">No Vehicles Registered</h5>
              <p class="small text-muted mb-3">Add your first car, motorcycle, SUV or truck to start scheduling maintenance.</p>
              <button type="button" class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#addVehicleModal">
                <i class="bi bi-plus-lg me-1"></i> Register Vehicle Now
              </button>
            </td>
          </tr>
        <?php else: ?>
          <?php foreach ($vehicles as $v): ?>
            <tr>
              <td>
                <div class="d-flex align-items-center gap-3">
                  <div class="p-2 rounded-3 bg-primary-subtle text-primary d-flex align-items-center justify-content-center" style="width: 42px; height: 42px;">
                    <?php if ($v['vehicle_type'] === 'Motorcycle'): ?>
                      <i class="bi bi-bicycle fs-5"></i>
                    <?php elseif ($v['vehicle_type'] === 'Truck'): ?>
                      <i class="bi bi-truck fs-5"></i>
                    <?php else: ?>
                      <i class="bi bi-car-front-fill fs-5"></i>
                    <?php endif; ?>
                  </div>
                  <div>
                    <div class="fw-bold text-dark fs-6"><?= escape($v['brand'] . ' ' . $v['model']) ?></div>
                    <small class="text-muted">Added <?= formatDate($v['created_at']) ?></small>
                  </div>
                </div>
              </td>
              <td>
                <span class="badge bg-secondary-subtle text-secondary border">
                  <?= escape($v['vehicle_type']) ?>
                </span>
              </td>
              <td>
                <span class="badge bg-dark text-white fw-bold px-2 py-1 font-monospace">
                  <?= escape($v['reg_number']) ?>
                </span>
              </td>
              <td><span class="fw-semibold text-dark"><?= escape($v['year']) ?></span></td>
              <td>
                <span class="badge bg-info-subtle text-info-emphasis border border-info-subtle">
                  <i class="bi bi-fuel-pump me-1"></i><?= escape($v['fuel_type']) ?>
                </span>
              </td>
              <td>
                <span class="badge bg-light text-dark border">
                  <?= $v['service_count'] ?> requests
                </span>
              </td>
              <td class="text-end">
                <div class="d-inline-flex gap-1">
                  <!-- Book Service for this vehicle -->
                  <a href="<?= url('customer/request_service.php?vehicle_id=' . $v['id']) ?>" class="btn btn-sm btn-outline-primary" title="Book Service">
                    <i class="bi bi-calendar-plus"></i>
                  </a>
                  
                  <!-- Edit Vehicle Button -->
                  <button type="button" class="btn btn-sm btn-outline-secondary edit-vehicle-btn" 
                          data-bs-toggle="modal" 
                          data-bs-target="#editVehicleModal"
                          data-id="<?= $v['id'] ?>"
                          data-type="<?= escape($v['vehicle_type']) ?>"
                          data-brand="<?= escape($v['brand']) ?>"
                          data-model="<?= escape($v['model']) ?>"
                          data-reg="<?= escape($v['reg_number']) ?>"
                          data-year="<?= escape($v['year']) ?>"
                          data-fuel="<?= escape($v['fuel_type']) ?>"
                          title="Edit Vehicle">
                    <i class="bi bi-pencil-square"></i>
                  </button>

                  <!-- Delete Vehicle Form with confirmation -->
                  <form action="<?= url('customer/vehicles.php') ?>" method="POST" class="d-inline">
                    <?php csrfField(); ?>
                    <input type="hidden" name="action" value="delete">
                    <input type="hidden" name="vehicle_id" value="<?= $v['id'] ?>">
                    <button type="button" class="btn btn-sm btn-outline-danger" 
                            data-confirm-action="delete" 
                            data-item-title="<?= escape($v['brand'] . ' ' . $v['model'] . ' (' . $v['reg_number'] . ')') ?>"
                            title="Delete Vehicle">
                      <i class="bi bi-trash3"></i>
                    </button>
                  </form>
                </div>
              </td>
            </tr>
          <?php endforeach; ?>
          <tr class="empty-filter-row" style="display: none;">
            <td colspan="7" class="text-center py-4 text-muted">
              <i class="bi bi-search me-1"></i> No vehicles found matching your search.
            </td>
          </tr>
        <?php endif; ?>
      </tbody>
    </table>
  </div>
</div>

<!-- ========================================== -->
<!-- ADD VEHICLE MODAL -->
<!-- ========================================== -->
<div class="modal fade" id="addVehicleModal" tabindex="-1" aria-labelledby="addVehicleModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content border-0 shadow">
      <div class="modal-header bg-dark text-white">
        <h5 class="modal-title fw-bold" id="addVehicleModalLabel">
          <i class="bi bi-plus-circle-fill text-primary me-2"></i>Register New Vehicle
        </h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>

      <form action="<?= url('customer/vehicles.php') ?>" method="POST" class="needs-validation" novalidate>
        <?php csrfField(); ?>
        <input type="hidden" name="action" value="add">

        <div class="modal-body p-4">
          <div class="row g-3">
            <div class="col-md-6">
              <label for="vehicle_type" class="form-label">Vehicle Type <span class="text-danger">*</span></label>
              <select class="form-select" id="vehicle_type" name="vehicle_type" required>
                <option value="">Select Type</option>
                <option value="Car">Car</option>
                <option value="SUV">SUV</option>
                <option value="Motorcycle">Motorcycle</option>
                <option value="Truck">Truck</option>
                <option value="Van">Van</option>
                <option value="Hatchback">Hatchback</option>
                <option value="Sedan">Sedan</option>
              </select>
              <div class="invalid-feedback">Please select a vehicle type.</div>
            </div>

            <div class="col-md-6">
              <label for="fuel_type" class="form-label">Fuel Type <span class="text-danger">*</span></label>
              <select class="form-select" id="fuel_type" name="fuel_type" required>
                <option value="">Select Fuel</option>
                <option value="Petrol">Petrol</option>
                <option value="Diesel">Diesel</option>
                <option value="Electric">Electric</option>
                <option value="Hybrid">Hybrid</option>
                <option value="CNG">CNG</option>
              </select>
              <div class="invalid-feedback">Please select fuel type.</div>
            </div>

            <div class="col-md-6">
              <label for="brand" class="form-label">Brand / Make <span class="text-danger">*</span></label>
              <input type="text" class="form-control" id="brand" name="brand" placeholder="e.g. Toyota, Honda" required>
              <div class="invalid-feedback">Brand is required.</div>
            </div>

            <div class="col-md-6">
              <label for="model" class="form-label">Model <span class="text-danger">*</span></label>
              <input type="text" class="form-control" id="model" name="model" placeholder="e.g. Corolla, Civic" required>
              <div class="invalid-feedback">Model is required.</div>
            </div>

            <div class="col-md-6">
              <label for="reg_number" class="form-label">Registration Number <span class="text-danger">*</span></label>
              <input type="text" class="form-control text-uppercase" id="reg_number" name="reg_number" placeholder="e.g. ABC-1234" required>
              <div class="invalid-feedback">Unique registration number is required.</div>
            </div>

            <div class="col-md-6">
              <label for="year" class="form-label">Manufacturing Year <span class="text-danger">*</span></label>
              <input type="number" class="form-control" id="year" name="year" min="1980" max="<?= date('Y') + 1 ?>" value="<?= date('Y') ?>" required>
              <div class="invalid-feedback">Enter a valid 4-digit year.</div>
            </div>
          </div>
        </div>

        <div class="modal-footer bg-light">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary">
            <i class="bi bi-check2-circle me-1"></i> Save Vehicle
          </button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- ========================================== -->
<!-- EDIT VEHICLE MODAL -->
<!-- ========================================== -->
<div class="modal fade" id="editVehicleModal" tabindex="-1" aria-labelledby="editVehicleModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content border-0 shadow">
      <div class="modal-header bg-dark text-white">
        <h5 class="modal-title fw-bold" id="editVehicleModalLabel">
          <i class="bi bi-pencil-square text-primary me-2"></i>Edit Vehicle Details
        </h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>

      <form action="<?= url('customer/vehicles.php') ?>" method="POST" class="needs-validation" novalidate>
        <?php csrfField(); ?>
        <input type="hidden" name="action" value="edit">
        <input type="hidden" name="vehicle_id" id="edit_vehicle_id" value="">

        <div class="modal-body p-4">
          <div class="row g-3">
            <div class="col-md-6">
              <label for="edit_vehicle_type" class="form-label">Vehicle Type <span class="text-danger">*</span></label>
              <select class="form-select" id="edit_vehicle_type" name="vehicle_type" required>
                <option value="Car">Car</option>
                <option value="SUV">SUV</option>
                <option value="Motorcycle">Motorcycle</option>
                <option value="Truck">Truck</option>
                <option value="Van">Van</option>
                <option value="Hatchback">Hatchback</option>
                <option value="Sedan">Sedan</option>
              </select>
            </div>

            <div class="col-md-6">
              <label for="edit_fuel_type" class="form-label">Fuel Type <span class="text-danger">*</span></label>
              <select class="form-select" id="edit_fuel_type" name="fuel_type" required>
                <option value="Petrol">Petrol</option>
                <option value="Diesel">Diesel</option>
                <option value="Electric">Electric</option>
                <option value="Hybrid">Hybrid</option>
                <option value="CNG">CNG</option>
              </select>
            </div>

            <div class="col-md-6">
              <label for="edit_brand" class="form-label">Brand / Make <span class="text-danger">*</span></label>
              <input type="text" class="form-control" id="edit_brand" name="brand" required>
            </div>

            <div class="col-md-6">
              <label for="edit_model" class="form-label">Model <span class="text-danger">*</span></label>
              <input type="text" class="form-control" id="edit_model" name="model" required>
            </div>

            <div class="col-md-6">
              <label for="edit_reg_number" class="form-label">Registration Number <span class="text-danger">*</span></label>
              <input type="text" class="form-control text-uppercase" id="edit_reg_number" name="reg_number" required>
            </div>

            <div class="col-md-6">
              <label for="edit_year" class="form-label">Manufacturing Year <span class="text-danger">*</span></label>
              <input type="number" class="form-control" id="edit_year" name="year" min="1980" max="<?= date('Y') + 1 ?>" required>
            </div>
          </div>
        </div>

        <div class="modal-footer bg-light">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary">
            <i class="bi bi-save me-1"></i> Update Changes
          </button>
        </div>
      </form>
    </div>
  </div>
</div>

<script>
// Populate Edit Modal on button click
document.addEventListener('DOMContentLoaded', function () {
  const editButtons = document.querySelectorAll('.edit-vehicle-btn');
  editButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      document.getElementById('edit_vehicle_id').value = this.getAttribute('data-id');
      document.getElementById('edit_vehicle_type').value = this.getAttribute('data-type');
      document.getElementById('edit_brand').value = this.getAttribute('data-brand');
      document.getElementById('edit_model').value = this.getAttribute('data-model');
      document.getElementById('edit_reg_number').value = this.getAttribute('data-reg');
      document.getElementById('edit_year').value = this.getAttribute('data-year');
      document.getElementById('edit_fuel_type').value = this.getAttribute('data-fuel');
    });
  });
});
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
