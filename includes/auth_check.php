<?php
/**
 * Vehicle Service Management System
 * Role-Based Authentication & Access Control
 */

require_once __DIR__ . '/../config/db.php';

/**
 * Require any logged-in user
 */
function requireLogin() {
    if (!isLoggedIn()) {
        setFlash('warning', 'Please sign in to access that page.');
        redirect('auth/login.php');
    }
}

/**
 * Require Customer role
 */
function requireCustomer() {
    requireLogin();
    if ($_SESSION['user_role'] !== 'customer') {
        setFlash('danger', 'Access denied. Customer dashboard only.');
        redirect('admin/dashboard.php');
    }
}

/**
 * Require Admin role
 */
function requireAdmin() {
    requireLogin();
    if ($_SESSION['user_role'] !== 'admin') {
        setFlash('danger', 'Access denied. Administrator privileges required.');
        redirect('customer/dashboard.php');
    }
}

/**
 * Generate CSRF Token
 * @return string
 */
function getCsrfToken() {
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

/**
 * Validate CSRF Token
 * @param string|null $token
 * @return bool
 */
function validateCsrfToken($token) {
    if (!isset($_SESSION['csrf_token']) || empty($token)) {
        return false;
    }
    return hash_equals($_SESSION['csrf_token'], $token);
}

/**
 * Render CSRF Hidden Input
 */
function csrfField() {
    echo '<input type="hidden" name="csrf_token" value="' . escape(getCsrfToken()) . '">';
}
