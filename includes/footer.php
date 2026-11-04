<?php
/**
 * Vehicle Service Management System
 * Global Footer Template
 */
$isDashboard = $isDashboard ?? false;
?>

<?php if ($isDashboard): ?>
    </main> <!-- /dashboard-main -->
  </div> <!-- /dashboard-wrapper -->
<?php else: ?>
  <!-- Public Footer -->
  <footer class="mt-auto bg-white py-4 border-top">
    <div class="container">
      <div class="row align-items-center gy-3">
        <div class="col-md-6 text-center text-md-start">
          <div class="d-flex align-items-center justify-content-center justify-content-md-start gap-2 mb-1">
            <span class="p-1 rounded bg-primary text-white d-inline-flex align-items-center justify-content-center" style="width: 24px; height: 24px;">
              <i class="bi bi-tools fs-6"></i>
            </span>
            <span class="fw-bold text-dark">VSM Pro</span>
          </div>
          <p class="text-muted small mb-0">&copy; <?= date('Y') ?> Vehicle Service Management System. All rights reserved.</p>
        </div>
        <div class="col-md-6 text-center text-md-end">
          <span class="badge bg-light text-secondary border me-2"><i class="bi bi-shield-check text-success me-1"></i>Secure PHP 8 PDO</span>
          <span class="badge bg-light text-secondary border"><i class="bi bi-database-check text-primary me-1"></i>MySQL / MariaDB</span>
        </div>
      </div>
    </div>
  </footer>
<?php endif; ?>

<!-- Universal Confirmation Modal (Delete & Cancel Dialogs) -->
<div class="modal fade" id="confirmationModal" tabindex="-1" aria-labelledby="confirmationModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content border-0 shadow">
      <div class="modal-header border-bottom-0 pb-0">
        <h5 class="modal-title fw-bold" id="confirmationModalLabel">Confirm Action</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body py-3">
        <p class="modal-body-content text-secondary mb-0">Are you sure you want to proceed with this action?</p>
      </div>
      <div class="modal-footer border-top-0 pt-0">
        <button type="button" class="btn btn-light" data-bs-dismiss="modal">Dismiss</button>
        <button type="button" class="btn btn-danger" id="confirmActionBtn">Proceed</button>
      </div>
    </div>
  </div>
</div>

<!-- Bootstrap 5 JS Bundle CDN -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>

<!-- Application Scripts -->
<script src="<?= url('assets/js/validation.js') ?>"></script>
<script src="<?= url('assets/js/main.js') ?>"></script>

</body>
</html>
