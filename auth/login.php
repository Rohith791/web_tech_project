<?php
/**
 * Vehicle Service Management System
 * User Login (Admin & Customer)
 */

require_once __DIR__ . '/../config/db.php';
require_once __DIR__ . '/../includes/auth_check.php';

// If already authenticated, redirect to role dashboard
if (isLoggedIn()) {
    redirect(isAdmin() ? 'admin/dashboard.php' : 'customer/dashboard.php');
}

$error = '';
$email = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = sanitize($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';
    $csrf = $_POST['csrf_token'] ?? '';

    if (!validateCsrfToken($csrf)) {
        $error = 'Security session expired. Please refresh and try again.';
    } elseif (empty($email) || empty($password)) {
        $error = 'Please enter both your email and password.';
    } else {
        $pdo = getDB();
        $stmt = $pdo->prepare("SELECT id, name, email, password_hash, role FROM users WHERE email = ? LIMIT 1");
        $stmt->execute([$email]);
        $user = $stmt->fetch();

        if ($user && password_verify($password, $user['password_hash'])) {
            // Regenerate session ID to prevent fixation
            session_regenerate_id(true);

            $_SESSION['user_id'] = $user['id'];
            $_SESSION['user_name'] = $user['name'];
            $_SESSION['user_email'] = $user['email'];
            $_SESSION['user_role'] = $user['role'];

            setFlash('success', 'Welcome back, ' . $user['name'] . '!');

            if ($user['role'] === 'admin') {
                redirect('admin/dashboard.php');
            } else {
                redirect('customer/dashboard.php');
            }
        } else {
            $error = 'Invalid email or password. Please try again.';
        }
    }
}

$pageTitle = 'Sign In';
$activeNav = 'login';
require_once __DIR__ . '/../includes/header.php';
?>

<div class="container py-5">
  <div class="row justify-content-center">
    <div class="col-md-7 col-lg-5">
      
      <div class="card shadow border-0 rounded-4 overflow-hidden mb-4">
        <div class="card-header bg-dark text-white p-4 text-center">
          <div class="mb-2">
            <span class="p-3 rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center">
              <i class="bi bi-shield-lock fs-3"></i>
            </span>
          </div>
          <h3 class="fw-bold mb-1 text-white">Sign In</h3>
          <p class="text-white-50 small mb-0">Access your customer account or administrator portal</p>
        </div>

        <div class="card-body p-4 p-md-5 bg-white">
          <?php if (!empty($error)): ?>
            <div class="alert alert-danger shadow-sm d-flex align-items-center" role="alert">
              <i class="bi bi-exclamation-triangle-fill me-2 fs-5"></i>
              <div><?= escape($error) ?></div>
            </div>
          <?php endif; ?>

          <form action="<?= url('auth/login.php') ?>" method="POST" class="needs-validation" novalidate>
            <?php csrfField(); ?>

            <div class="mb-3">
              <label for="loginEmail" class="form-label">Email Address</label>
              <div class="input-group">
                <span class="input-group-text bg-light"><i class="bi bi-envelope"></i></span>
                <input type="email" class="form-control" id="loginEmail" name="email" placeholder="name@example.com" value="<?= escape($email) ?>" required>
                <div class="invalid-feedback">Please enter a valid email address.</div>
              </div>
            </div>

            <div class="mb-4">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <label for="loginPassword" class="form-label mb-0">Password</label>
              </div>
              <div class="input-group">
                <span class="input-group-text bg-light"><i class="bi bi-lock"></i></span>
                <input type="password" class="form-control" id="loginPassword" name="password" placeholder="••••••••" required>
                <div class="invalid-feedback">Please enter your password.</div>
              </div>
            </div>

            <button type="submit" class="btn btn-primary w-100 py-2 fs-6 shadow-sm mb-3">
              <i class="bi bi-box-arrow-in-right me-1"></i> Sign In to Account
            </button>
          </form>

          <div class="text-center text-muted small pt-2 border-top">
            Don't have an account yet? 
            <a href="<?= url('auth/register.php') ?>" class="text-primary fw-bold text-decoration-none ms-1">
              Create an Account <i class="bi bi-arrow-right-short"></i>
            </a>
          </div>
        </div>
      </div>

      <!-- Quick Demo Credentials Card -->
      <div class="card border-0 bg-white shadow-sm p-3 rounded-3">
        <h6 class="fw-bold text-secondary mb-2 small text-uppercase"><i class="bi bi-key-fill text-warning me-1"></i> Quick Demo Logins</h6>
        <div class="row g-2">
          <div class="col-6">
            <button type="button" class="btn btn-outline-dark btn-sm w-100 text-start py-2" onclick="fillLogin('admin@vsm.com', 'admin123')">
              <div class="fw-bold small"><i class="bi bi-person-badge-fill text-danger me-1"></i> Admin</div>
              <div class="text-muted" style="font-size: 0.72rem;">admin@vsm.com</div>
            </button>
          </div>
          <div class="col-6">
            <button type="button" class="btn btn-outline-dark btn-sm w-100 text-start py-2" onclick="fillLogin('john@example.com', 'customer123')">
              <div class="fw-bold small"><i class="bi bi-person-fill text-primary me-1"></i> Customer</div>
              <div class="text-muted" style="font-size: 0.72rem;">john@example.com</div>
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</div>

<script>
function fillLogin(email, password) {
  document.getElementById('loginEmail').value = email;
  document.getElementById('loginPassword').value = password;
}
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
