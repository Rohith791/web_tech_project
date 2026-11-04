-- Vehicle Service Management System
-- Database Schema & Initial Seed Data

CREATE DATABASE IF NOT EXISTS `vehicle_service_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `vehicle_service_db`;

-- Drop tables if they already exist (in reverse FK order)
DROP TABLE IF EXISTS `service_requests`;
DROP TABLE IF EXISTS `vehicles`;
DROP TABLE IF EXISTS `services`;
DROP TABLE IF EXISTS `users`;

-- 1. Users Table
CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(150) NOT NULL UNIQUE,
  `phone` VARCHAR(15) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `address` TEXT NULL,
  `role` ENUM('customer', 'admin') NOT NULL DEFAULT 'customer',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_users_role` (`role`),
  INDEX `idx_users_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Vehicles Table
CREATE TABLE `vehicles` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `vehicle_type` VARCHAR(50) NOT NULL,
  `brand` VARCHAR(60) NOT NULL,
  `model` VARCHAR(60) NOT NULL,
  `reg_number` VARCHAR(30) NOT NULL UNIQUE,
  `year` INT NOT NULL,
  `fuel_type` VARCHAR(30) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_vehicles_user_id` (`user_id`),
  INDEX `idx_vehicles_reg` (`reg_number`),
  CONSTRAINT `fk_vehicles_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Services Table
CREATE TABLE `services` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `service_name` VARCHAR(100) NOT NULL,
  `description` TEXT NOT NULL,
  `base_price` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Service Requests Table
CREATE TABLE `service_requests` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `vehicle_id` INT NOT NULL,
  `service_id` INT NOT NULL,
  `preferred_date` DATE NOT NULL,
  `description` TEXT NULL,
  `status` ENUM('Pending', 'In Progress', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Pending',
  `admin_remark` TEXT NULL,
  `cost` DECIMAL(10, 2) NULL DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_requests_user` (`user_id`),
  INDEX `idx_requests_vehicle` (`vehicle_id`),
  INDEX `idx_requests_service` (`service_id`),
  INDEX `idx_requests_status` (`status`),
  CONSTRAINT `fk_requests_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_requests_vehicle` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_requests_service` FOREIGN KEY (`service_id`) REFERENCES `services` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===================================================
-- SEED DATA
-- Default Passwords:
-- Admin (admin@vsm.com): admin123
-- Customers (john@example.com, sarah@example.com): customer123
-- ===================================================

-- Seed Users
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password_hash`, `address`, `role`, `created_at`) VALUES
(1, 'System Administrator', 'admin@vsm.com', '9876543210', '$2y$10$nrZ2lyhJOCJYFBs4qw7K3.JujozrCMN4HRTnh6jPEpB6Ih8/t2Qkq', 'VSM Service HQ, Central Avenue, Tech Park', 'admin', NOW()),
(2, 'John Doe', 'john@example.com', '9876543211', '$2y$10$GKgW87LUKMgvrlJWkVlfm./2iBI3mzh3CPi8s.Y79Mu15Mputk1wO', '42 Elm Street, Springfield', 'customer', NOW()),
(3, 'Sarah Connor', 'sarah@example.com', '9876543212', '$2y$10$GKgW87LUKMgvrlJWkVlfm./2iBI3mzh3CPi8s.Y79Mu15Mputk1wO', '77 Highland Park, Cyber City', 'customer', NOW());

-- Seed Services
INSERT INTO `services` (`id`, `service_name`, `description`, `base_price`) VALUES
(1, 'General Service', 'Complete comprehensive checkup, fluid top-up, spark plug inspection, filter clean, and road test.', 120.00),
(2, 'Oil & Filter Change', 'Premium synthetic engine oil replacement with OEM grade oil filter replacement and lube service.', 55.00),
(3, 'Brake Repair & Inspection', 'Front and rear brake pads inspection, disc skimming or replacement, rotor check, and brake bleed.', 85.00),
(4, 'Engine Diagnostics & Repair', 'Advanced computer scan diagnosis, sensor diagnostics, fuel system test, and performance tune-up.', 250.00),
(5, 'Complete Car Spa & Washing', 'Exterior snow foam pressure wash, interior deep vacuum, upholstery steam clean, and tire dressing.', 40.00),
(6, 'Tyre Replacement & Balancing', 'Tread inspection, computerized dynamic wheel balancing, rotation, and high-performance tire fitting.', 95.00);

-- Seed Vehicles
INSERT INTO `vehicles` (`id`, `user_id`, `vehicle_type`, `brand`, `model`, `reg_number`, `year`, `fuel_type`, `created_at`) VALUES
(1, 2, 'Car', 'Honda', 'Civic EX', 'ABC-1024', 2021, 'Petrol', NOW()),
(2, 2, 'Motorcycle', 'Yamaha', 'MT-15 V2', 'YAM-7788', 2023, 'Petrol', NOW()),
(3, 3, 'Car', 'Tesla', 'Model 3 Dual Motor', 'EV-9900', 2022, 'Electric', NOW()),
(4, 3, 'SUV', 'Toyota', 'RAV4 Hybrid', 'RAV-4040', 2020, 'Hybrid', NOW());

-- Seed Service Requests
INSERT INTO `service_requests` (`id`, `user_id`, `vehicle_id`, `service_id`, `preferred_date`, `description`, `status`, `admin_remark`, `cost`, `created_at`, `updated_at`) VALUES
(1, 2, 1, 1, DATE_ADD(CURRENT_DATE, INTERVAL -5 DAY), 'Regular 20,000 km periodic service required.', 'Completed', 'Full general service completed. Replaced engine air filter and topped up coolant.', 135.00, DATE_ADD(NOW(), INTERVAL -6 DAY), DATE_ADD(NOW(), INTERVAL -4 DAY)),
(2, 2, 2, 2, DATE_ADD(CURRENT_DATE, INTERVAL 1 DAY), 'Change engine oil with 10W-40 Motul synthetic.', 'In Progress', 'Bike mounted on bay 3. Oil drained, waiting for fresh filter batch.', 60.00, DATE_ADD(NOW(), INTERVAL -1 DAY), NOW()),
(3, 3, 3, 5, DATE_ADD(CURRENT_DATE, INTERVAL 3 DAY), 'Complete interior detailing before weekend trip.', 'Pending', NULL, NULL, NOW(), NOW()),
(4, 3, 4, 3, DATE_ADD(CURRENT_DATE, INTERVAL -2 DAY), 'Slight squeaking sound from front brakes when decelerating.', 'Cancelled', 'Cancelled as per customer telephone request; vehicle sold.', 0.00, DATE_ADD(NOW(), INTERVAL -3 DAY), DATE_ADD(NOW(), INTERVAL -2 DAY));
