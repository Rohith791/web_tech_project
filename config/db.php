<?php
/**
 * Vehicle Service Management System
 * Database Configuration & Core Utilities
 */

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// Database Credentials
define('DB_HOST', '127.0.0.1');
define('DB_NAME', 'vehicle_service_db');
define('DB_USER', 'root');
define('DB_PASS', '');
define('DB_CHARSET', 'utf8mb4');

/**
 * Get PDO Database Connection (Singleton)
 * @return PDO
 */
function getDB() {
    static $pdo = null;
    if ($pdo === null) {
        $dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=" . DB_CHARSET;
        $options = [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false,
        ];
        try {
            $pdo = new PDO($dsn, DB_USER, DB_PASS, $options);
        } catch (PDOException $e) {
            die("Database connection failed: " . htmlspecialchars($e->getMessage(), ENT_QUOTES, 'UTF-8'));
        }
    }
    return $pdo;
}

// Automatically detect application base URL
if (!defined('BASE_URL')) {
    $scriptDir = isset($_SERVER['SCRIPT_NAME']) ? str_replace('\\', '/', dirname($_SERVER['SCRIPT_NAME'])) : '';
    // Strip subfolders like /auth, /customer, /admin, /includes to find root
    $root = preg_replace('#/(auth|customer|admin|includes)(/.*)?$#i', '', $scriptDir);
    $root = rtrim($root, '/');
    define('BASE_URL', $root);
}

/**
 * Generate absolute URL for application paths
 * @param string $path
 * @return string
 */
function url($path = '') {
    $path = ltrim($path, '/');
    return (BASE_URL === '' ? '' : BASE_URL) . '/' . $path;
}

/**
 * Escape HTML output to prevent XSS
 * @param mixed $data
 * @return string
 */
function escape($data) {
    if ($data === null) {
        return '';
    }
    return htmlspecialchars((string)$data, ENT_QUOTES, 'UTF-8');
}

/**
 * Sanitize input string
 * @param mixed $data
 * @return string
 */
function sanitize($data) {
    if (is_array($data)) {
        return array_map('sanitize', $data);
    }
    return trim((string)$data);
}

/**
 * Set flash alert message
 * @param string $type success|danger|warning|info
 * @param string $message
 */
function setFlash($type, $message) {
    $_SESSION['flash'] = [
        'type' => $type,
        'message' => $message
    ];
}

/**
 * Get and clear flash message
 * @return array|null
 */
function getFlash() {
    if (isset($_SESSION['flash'])) {
        $flash = $_SESSION['flash'];
        unset($_SESSION['flash']);
        return $flash;
    }
    return null;
}

/**
 * Render Flash Alert HTML
 */
function displayFlash() {
    $flash = getFlash();
    if ($flash) {
        $type = escape($flash['type']);
        $icon = 'bi-info-circle-fill';
        if ($type === 'success') $icon = 'bi-check-circle-fill';
        if ($type === 'danger') $icon = 'bi-exclamation-triangle-fill';
        if ($type === 'warning') $icon = 'bi-exclamation-circle-fill';
        
        echo '<div class="alert alert-' . $type . ' alert-dismissible fade show shadow-sm d-flex align-items-center" role="alert">';
        echo '  <i class="bi ' . $icon . ' me-2 fs-5"></i>';
        echo '  <div class="flex-grow-1">' . escape($flash['message']) . '</div>';
        echo '  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
        echo '</div>';
    }
}

/**
 * Check if a user is logged in
 * @return bool
 */
function isLoggedIn() {
    return isset($_SESSION['user_id']) && !empty($_SESSION['user_id']);
}

/**
 * Check if the logged-in user is an admin
 * @return bool
 */
function isAdmin() {
    return isLoggedIn() && isset($_SESSION['user_role']) && $_SESSION['user_role'] === 'admin';
}

/**
 * Check if the logged-in user is a customer
 * @return bool
 */
function isCustomer() {
    return isLoggedIn() && isset($_SESSION['user_role']) && $_SESSION['user_role'] === 'customer';
}

/**
 * Safe redirect helper
 * @param string $path
 */
function redirect($path) {
    header("Location: " . url($path));
    exit;
}

/**
 * Render Status Badge
 * @param string $status
 * @return string
 */
function statusBadge($status) {
    $status = trim($status);
    switch ($status) {
        case 'Pending':
            return '<span class="badge bg-warning-subtle text-warning-emphasis border border-warning-subtle px-2 py-1"><i class="bi bi-clock-history me-1"></i>Pending</span>';
        case 'In Progress':
            return '<span class="badge bg-primary-subtle text-primary-emphasis border border-primary-subtle px-2 py-1"><i class="bi bi-gear-wide-connected me-1"></i>In Progress</span>';
        case 'Completed':
            return '<span class="badge bg-success-subtle text-success-emphasis border border-success-subtle px-2 py-1"><i class="bi bi-check-circle-fill me-1"></i>Completed</span>';
        case 'Cancelled':
            return '<span class="badge bg-danger-subtle text-danger-emphasis border border-danger-subtle px-2 py-1"><i class="bi bi-x-circle-fill me-1"></i>Cancelled</span>';
        default:
            return '<span class="badge bg-secondary-subtle text-secondary-emphasis border border-secondary-subtle px-2 py-1">' . escape($status) . '</span>';
    }
}

/**
 * Format Currency
 * @param float|null $amount
 * @return string
 */
function formatCurrency($amount) {
    if ($amount === null || $amount === '') {
        return '—';
    }
    return '$' . number_format((float)$amount, 2);
}

/**
 * Format Date
 * @param string|null $date
 * @return string
 */
function formatDate($date) {
    if (!$date) return '—';
    return date('M d, Y', strtotime($date));
}
