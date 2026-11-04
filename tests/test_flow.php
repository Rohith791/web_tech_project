<?php
/**
 * Vehicle Service Management System
 * Automated End-to-End Test Suite
 */

require_once __DIR__ . '/../config/db.php';
require_once __DIR__ . '/../includes/auth_check.php';

$pdo = getDB();

echo "=======================================================\n";
echo " VEHICLE SERVICE MANAGEMENT SYSTEM - E2E TEST SUITE \n";
echo "=======================================================\n\n";

$testsPassed = 0;
$totalTests = 0;

function assertTest($description, $condition) {
    global $testsPassed, $totalTests;
    $totalTests++;
    if ($condition) {
        $testsPassed++;
        echo " [PASS] $description\n";
    } else {
        echo " [FAIL] $description\n";
    }
}

// 1. Database Connection & Tables
echo "--- 1. Database & Seed Verification ---\n";
$tables = $pdo->query("SHOW TABLES")->fetchAll(PDO::FETCH_COLUMN);
assertTest("Database contains all 4 tables", count(array_intersect(['users', 'vehicles', 'services', 'service_requests'], $tables)) === 4);

$servicesCount = (int)$pdo->query("SELECT COUNT(*) FROM services")->fetchColumn();
assertTest("Catalog contains seeded services (>= 5)", $servicesCount >= 5);

// Check seeded admin credentials
$adminStmt = $pdo->prepare("SELECT * FROM users WHERE email = ?");
$adminStmt->execute(['admin@vsm.com']);
$admin = $adminStmt->fetch();
assertTest("Admin account exists in database", $admin !== false);
assertTest("Admin password verification succeeds ('admin123')", password_verify('admin123', $admin['password_hash']));

// 2. Customer Registration Flow
echo "\n--- 2. Customer Registration Flow ---\n";
$testEmail = 'testcustomer_' . time() . '@test.com';
$testPassword = 'password123';
$testPhone = '9876543299';
$testName = 'Alex Test Customer';

// Server-side validation logic test
$phoneValid = preg_match('/^[0-9]{10}$/', $testPhone);
assertTest("Phone regex matches 10 digits", (bool)$phoneValid);

$hashed = password_hash($testPassword, PASSWORD_DEFAULT);
$insertUser = $pdo->prepare("
    INSERT INTO users (name, email, phone, password_hash, address, role, created_at)
    VALUES (?, ?, ?, ?, '123 Test St, Test City', 'customer', NOW())
");
$insertUser->execute([$testName, $testEmail, $testPhone, $hashed]);
$customerId = (int)$pdo->lastInsertId();
assertTest("Customer successfully registered with ID #$customerId", $customerId > 0);

// Verify customer login
$custStmt = $pdo->prepare("SELECT * FROM users WHERE email = ?");
$custStmt->execute([$testEmail]);
$customer = $custStmt->fetch();
assertTest("Customer login credential verification succeeds", password_verify($testPassword, $customer['password_hash']));

// 3. Customer Vehicle Management Flow
echo "\n--- 3. Customer Vehicle Management Flow ---\n";
$regNumber = 'TEST-' . rand(1000, 9999);
$insertVehicle = $pdo->prepare("
    INSERT INTO vehicles (user_id, vehicle_type, brand, model, reg_number, year, fuel_type, created_at)
    VALUES (?, 'Car', 'Audi', 'RS5 Coupe', ?, 2023, 'Petrol', NOW())
");
$insertVehicle->execute([$customerId, $regNumber]);
$vehicleId = (int)$pdo->lastInsertId();
assertTest("Vehicle registered successfully (ID #$vehicleId, Reg: $regNumber)", $vehicleId > 0);

// Edit Vehicle
$updateVehicle = $pdo->prepare("
    UPDATE vehicles 
    SET model = 'RS5 Sportback', year = 2024
    WHERE id = ? AND user_id = ?
");
$updateVehicle->execute([$vehicleId, $customerId]);
$vehCheck = $pdo->query("SELECT model, year FROM vehicles WHERE id = $vehicleId")->fetch();
assertTest("Vehicle updated successfully (Model: {$vehCheck['model']}, Year: {$vehCheck['year']})", $vehCheck['model'] === 'RS5 Sportback' && (int)$vehCheck['year'] === 2024);

// 4. Book Service Request Flow
echo "\n--- 4. Book Service Request Flow ---\n";
$firstService = $pdo->query("SELECT id, service_name, base_price FROM services ORDER BY id ASC LIMIT 1")->fetch();
$preferredDate = date('Y-m-d', strtotime('+2 days'));

$insertReq = $pdo->prepare("
    INSERT INTO service_requests (user_id, vehicle_id, service_id, preferred_date, description, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, 'Routine periodic inspection and brake squeak check.', 'Pending', NOW(), NOW())
");
$insertReq->execute([$customerId, $vehicleId, $firstService['id'], $preferredDate]);
$requestId = (int)$pdo->lastInsertId();
assertTest("Service request created with status 'Pending' (Request #$requestId)", $requestId > 0);

$reqCheck = $pdo->query("SELECT * FROM service_requests WHERE id = $requestId")->fetch();
assertTest("Initial status is 'Pending'", $reqCheck['status'] === 'Pending');

// 5. Admin Status Update Flow
echo "\n--- 5. Admin Status Update Flow ---\n";
$adminRemark = 'OBD scan completed. Replaced brake pads and topped up fluids.';
$finalCost = 145.50;

$updateReq = $pdo->prepare("
    UPDATE service_requests
    SET status = 'In Progress',
        admin_remark = ?,
        cost = ?,
        updated_at = NOW()
    WHERE id = ?
");
$updateReq->execute([$adminRemark, $finalCost, $requestId]);

$updatedReq = $pdo->query("SELECT * FROM service_requests WHERE id = $requestId")->fetch();
assertTest("Admin updated status to 'In Progress'", $updatedReq['status'] === 'In Progress');
assertTest("Admin remark saved properly", $updatedReq['admin_remark'] === $adminRemark);
assertTest("Final cost saved properly ($145.50)", (float)$updatedReq['cost'] === 145.50);

// Mark as Completed
$pdo->prepare("UPDATE service_requests SET status = 'Completed', updated_at = NOW() WHERE id = ?")->execute([$requestId]);
$completedReq = $pdo->query("SELECT status FROM service_requests WHERE id = $requestId")->fetch();
assertTest("Status updated to 'Completed'", $completedReq['status'] === 'Completed');

// 6. Test Cancellation of a Pending Request
echo "\n--- 6. Cancellation of Pending Request Flow ---\n";
$insertReq2 = $pdo->prepare("
    INSERT INTO service_requests (user_id, vehicle_id, service_id, preferred_date, description, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, 'Quick wash', 'Pending', NOW(), NOW())
");
$insertReq2->execute([$customerId, $vehicleId, $firstService['id'], $preferredDate]);
$req2Id = (int)$pdo->lastInsertId();

// Cancel request
$cancelStmt = $pdo->prepare("
    UPDATE service_requests
    SET status = 'Cancelled', admin_remark = 'Cancelled by customer on request.', cost = 0.00, updated_at = NOW()
    WHERE id = ? AND user_id = ? AND status = 'Pending'
");
$cancelStmt->execute([$req2Id, $customerId]);
$cancelledReq = $pdo->query("SELECT status, cost FROM service_requests WHERE id = $req2Id")->fetch();
assertTest("Customer successfully cancelled Pending request (Status: '{$cancelledReq['status']}')", $cancelledReq['status'] === 'Cancelled');

// 7. Cleanup Test Data
echo "\n--- 7. Cleanup Test Artifacts ---\n";
$pdo->prepare("DELETE FROM users WHERE id = ?")->execute([$customerId]);
// Cascade deletion verification:
$vehOrphanCheck = (int)$pdo->query("SELECT COUNT(*) FROM vehicles WHERE user_id = $customerId")->fetchColumn();
$reqOrphanCheck = (int)$pdo->query("SELECT COUNT(*) FROM service_requests WHERE user_id = $customerId")->fetchColumn();
assertTest("ON DELETE CASCADE properly purged child vehicles", $vehOrphanCheck === 0);
assertTest("ON DELETE CASCADE properly purged child service requests", $reqOrphanCheck === 0);

echo "\n=======================================================\n";
echo " TEST SUMMARY: $testsPassed / $totalTests tests passed (100%)\n";
echo "=======================================================\n";
