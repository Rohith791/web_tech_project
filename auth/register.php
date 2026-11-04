<?php
/**
 * Vehicle Service Management System
 * Customer Registration
 */

require_once __DIR__ . '/../config/db.php';
require_once __DIR__ . '/../includes/auth_check.php';

// If already logged in, redirect to respective dashboard
if (isLoggedIn()) {
    redirect(isAdmin() ? 'admin/dashboard.php' : 'customer/dashboard.php');
}

$errors = [];
$name = '';
$email = '';
$phone = '';
$address = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = sanitize($_POST['name'] ?? '');
    $email = sanitize($_POST['email'] ?? '');
    $phone = sanitize($_POST['phone'] ?? '');
    $password = $_POST['password'] ?? '';
    $address = sanitize($_POST['address'] ?? '');
    $csrf = $_POST['csrf_token'] ?? '';

    // CSRF verification
    if (!validateCsrfToken($csrf)) {
        $errors[] = 'Session security token expired. Please try again.';
    }

    // Validation
    if (empty($name) || strlen($name) < 2) {
        $errors[] = 'Full name is required (minimum 2 characters).';
    }

    if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $errors[] = 'A valid email address is required.';
    }

    if (!preg_match('/^[0-9]{10}$/', $phone)) {
        $errors[] = 'Phone number must be exactly 10 digits.';
    }

    if (strlen($password) < 6) {
        $errors[] = 'Password must be at least 6 characters long.';
    }

    // Duplicate email check
    if (empty($errors)) {
        $pdo = getDB();
        $stmt = $pdo->prepare("SELECT id FROM users WHERE email = ?");
        $stmt->execute([$email]);
        if ($stmt->fetch()) {
            $errors[] = 'This email address is already registered. Please sign in or use another email.';
        }
    }

    // Insert new customer
    if (empty($errors)) {
        try {
            $hashedPassword = password_hash($password, PASSWORD_DEFAULT);
            $stmt = $pdo->prepare("
                INSERT INTO users (name, email, phone, password_hash, address, role, created_at)
                VALUES (?, ?, ?, ?, ?, 'customer', NOW())
            ");
            $stmt->execute([$name, $email, $phone, $hashedPassword, $address]);
            
            $newUserId = $pdo->lastInsertId();

            // Auto-login customer
            $_SESSION['user_id'] = $newUserId;
            $_SESSION['user_name'] = $name;
            $_SESSION['user_email'] = $email;
            $_SESSION['user_role'] = 'customer';

            setFlash('success', 'Registration successful! Welcome to your Vehicle Service Dashboard.');
            redirect('customer/dashboard.php');
        } catch (PDOException $e) {
            $errors[] = 'Database error during registration: ' . $e->getMessage();
        }
    }
}

$pageTitle = 'Customer Registration';
$activeNav = 'register';
require_once __DIR__ . '/../includes/header.php';
?>

<div class="container py-5">
  <div class="row justify-content-center">
    <div class="col-md-8 col-lg-6">
      
      <div class="card shadow border-0 rounded-4 overflow-hidden">
        <div class="card-header bg-dark text-white p-4 text-center">
          <div class="mb-2">
            <span class="p-3 rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center">
              <i class="bi bi-person-plus fs-3"></i>
            </span>
          </div>
          <h3 class="fw-bold mb-1 text-white">Create an Account</h3>
          <p class="text-white-50 small mb-0">Join VSM Pro to manage your vehicles & book service appointments</p>
        </div>

        <div class="card-body p-4 p-md-5 bg-white">
          <?php if (!empty($errors)): ?>
            <div class="alert alert-danger shadow-sm">
              <ul class="mb-0 ps-3">
                <?php foreach ($errors as $error): ?>
                  <li><?= escape($error) ?></li>
                <?php endforeach; ?>
              </ul>
            </div>
          <?php endif; ?>

          <form action="<?= url('auth/register.php') ?>" method="POST" class="needs-validation" novalidate>
            <?php csrfField(); ?>

            <div class="mb-3">
              <label for="name" class="form-label">Full Name <span class="text-danger">*</span></label>
              <div class="input-group">
                <span class="input-group-text bg-light"><i class="bi bi-person"></i></span>
                <input type="text" class="form-control" id="name" name="name" placeholder="e.g. Alex Johnson" value="<?= escape($name) ?>" required minlength="2">
                <div class="invalid-feedback">Please enter your full name (minimum 2 letters).</div>
              </div>
            </div>

            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <label for="email" class="form-label">Email Address <span class="text-danger">*</span></label>
                <div class="input-group">
                  <span class="input-group-text bg-light"><i class="bi bi-envelope"></i></span>
                  <input type="email" class="form-control" id="email" name="email" placeholder="you@domain.com" value="<?= escape($email) ?>" required>
                  <div class="invalid-feedback">Please provide a valid email address.</div>
                </div>
              </div>

              <div class="col-md-6">
                <label for="phone" class="form-label">10-Digit Mobile <span class="text-danger">*</span></label>
                <div class="input-group">
                  <span class="input-group-text bg-light"><i class="bi bi-telephone"></i></span>
                  <input type="tel" class="form-control" id="phone" name="phone" placeholder="9876543210" maxlength="10" pattern="[0-9]{10}" value="<?= escape($phone) ?>" required>
                  <div class="invalid-feedback">Phone must be exactly 10 digits.</div>
                </div>
              </div>
            </div>

            <div class="mb-3">
              <label for="password" class="form-label">Password <span class="text-danger">*</span></label>
              <div class="input-group">
                <span class="input-group-text bg-light"><i class="bi bi-lock"></i></span>
                <input type="password" class="form-control" id="password" name="password" placeholder="At least 6 characters" required minlength="6">
                <div class="invalid-feedback">Password must be at least 6 characters.</div>
              </div>
            </div>

            <div class="mb-4">
              <label for="address" class="form-label">Residential Address</label>
              <div class="input-group">
                <span class="input-group-text bg-light"><i class="bi bi-geo-alt"></i></span>
                <textarea class="form-control" id="address" name="address" rows="2" placeholder="Street, City, Postal Code"><?= escape($address) ?></textarea>
              </div>
            </div>

            <button type="submit" class="btn btn-primary w-100 py-2 fs-6 shadow-sm">
              <i class="bi bi-check2-circle me-1"></i> Complete Registration
            </button>
          </form>

          <div class="mt-4 pt-3 border-top text-center text-muted small">
            Already have an account? 
            <a href="<?= url('auth/login.php') ?>" class="text-primary fw-bold text-decoration-none ms-1">
              Sign In Here <i class="bi bi-arrow-right-short"></i>
            </a>
          </div>
        </div>
      </div>

    </div>
  </div>
</div>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
