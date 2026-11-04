/**
 * Vehicle Service Management System
 * Main Frontend Interactions & Table Filtering
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Sidebar Toggle for Mobile
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.sidebar-overlay');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('show');
      if (overlay) overlay.classList.toggle('show');
    });
  }

  if (overlay && sidebar) {
    overlay.addEventListener('click', function () {
      sidebar.classList.remove('show');
      overlay.classList.remove('show');
    });
  }

  // 2. Auto-dismiss flash alerts after 5 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 6000);
  });

  // 3. Generic Client-side Table Filter & Search
  // Looks for input[data-table-search="tableId"] and select[data-table-filter="tableId"]
  const searchInputs = document.querySelectorAll('[data-table-search]');
  searchInputs.forEach(searchInput => {
    const tableId = searchInput.getAttribute('data-table-search');
    const table = document.getElementById(tableId);
    if (!table) return;

    const filterSelect = document.querySelector(`[data-table-filter="${tableId}"]`);

    function applyFilter() {
      const query = searchInput.value.toLowerCase().trim();
      const selectedStatus = filterSelect ? filterSelect.value.toLowerCase().trim() : '';
      const rows = table.querySelectorAll('tbody tr:not(.no-filter)');

      let visibleCount = 0;
      rows.forEach(row => {
        const rowText = row.innerText.toLowerCase();
        const rowStatus = (row.getAttribute('data-status') || '').toLowerCase();

        const matchesQuery = query === '' || rowText.includes(query);
        const matchesStatus = selectedStatus === '' || selectedStatus === 'all' || rowStatus === selectedStatus;

        if (matchesQuery && matchesStatus) {
          row.style.display = '';
          visibleCount++;
        } else {
          row.style.display = 'none';
        }
      });

      // Show or hide "No records match" placeholder row if available
      const emptyRow = table.querySelector('.empty-filter-row');
      if (emptyRow) {
        emptyRow.style.display = (visibleCount === 0 && rows.length > 0) ? '' : 'none';
      }
    }

    searchInput.addEventListener('input', applyFilter);
    if (filterSelect) {
      filterSelect.addEventListener('change', applyFilter);
    }
  });

  // 4. Status Filter Buttons (e.g., in Customer History tabs)
  const filterButtons = document.querySelectorAll('[data-status-btn]');
  filterButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      filterButtons.forEach(b => b.classList.remove('active', 'btn-primary'));
      filterButtons.forEach(b => b.classList.add('btn-outline-secondary'));
      this.classList.add('active', 'btn-primary');
      this.classList.remove('btn-outline-secondary');

      const status = this.getAttribute('data-status-btn').toLowerCase();
      const tableId = this.getAttribute('data-target-table');
      const table = document.getElementById(tableId);
      if (!table) return;

      const rows = table.querySelectorAll('tbody tr:not(.no-filter)');
      let visibleCount = 0;
      rows.forEach(row => {
        const rowStatus = (row.getAttribute('data-status') || '').toLowerCase();
        if (status === 'all' || rowStatus === status) {
          row.style.display = '';
          visibleCount++;
        } else {
          row.style.display = 'none';
        }
      });

      const emptyRow = table.querySelector('.empty-filter-row');
      if (emptyRow) {
        emptyRow.style.display = (visibleCount === 0 && rows.length > 0) ? '' : 'none';
      }
    });
  });

  // 5. Dynamic Service details on Request Service page
  const serviceSelect = document.getElementById('service_id');
  const servicePriceDisplay = document.getElementById('servicePriceDisplay');
  const serviceDescDisplay = document.getElementById('serviceDescDisplay');
  const servicePriceAlert = document.getElementById('servicePriceAlert');

  if (serviceSelect && servicePriceDisplay) {
    serviceSelect.addEventListener('change', function () {
      const selectedOption = this.options[this.selectedIndex];
      if (selectedOption && selectedOption.value) {
        const price = selectedOption.getAttribute('data-price') || '0.00';
        const desc = selectedOption.getAttribute('data-desc') || '';
        servicePriceDisplay.textContent = '$' + parseFloat(price).toFixed(2);
        if (serviceDescDisplay) serviceDescDisplay.textContent = desc;
        if (servicePriceAlert) servicePriceAlert.classList.remove('d-none');
      } else {
        if (servicePriceAlert) servicePriceAlert.classList.add('d-none');
      }
    });
  }

  // 6. Generic Confirmation Modal Handlers (for Delete and Cancel)
  const confirmModalEl = document.getElementById('confirmationModal');
  if (confirmModalEl) {
    const confirmModal = new bootstrap.Modal(confirmModalEl);
    const modalTitle = confirmModalEl.querySelector('.modal-title');
    const modalBody = confirmModalEl.querySelector('.modal-body-content');
    const confirmBtn = document.getElementById('confirmActionBtn');
    let targetForm = null;

    document.querySelectorAll('[data-confirm-action]').forEach(btn => {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        targetForm = this.closest('form');
        const actionType = this.getAttribute('data-confirm-action'); // 'delete' or 'cancel'
        const itemTitle = this.getAttribute('data-item-title') || 'this item';

        if (actionType === 'delete') {
          modalTitle.innerHTML = '<i class="bi bi-trash3-fill text-danger me-2"></i>Confirm Deletion';
          modalBody.innerHTML = `Are you sure you want to delete <strong>${itemTitle}</strong>? This action cannot be undone and will delete associated history.`;
          confirmBtn.className = 'btn btn-danger';
          confirmBtn.innerHTML = '<i class="bi bi-trash3 me-1"></i>Delete Now';
        } else if (actionType === 'cancel') {
          modalTitle.innerHTML = '<i class="bi bi-x-circle-fill text-warning me-2"></i>Cancel Service Request';
          modalBody.innerHTML = `Are you sure you want to cancel service request <strong>${itemTitle}</strong>?`;
          confirmBtn.className = 'btn btn-warning';
          confirmBtn.innerHTML = '<i class="bi bi-x-lg me-1"></i>Yes, Cancel Request';
        }

        confirmModal.show();
      });
    });

    if (confirmBtn) {
      confirmBtn.addEventListener('click', function () {
        if (targetForm) {
          targetForm.submit();
        }
      });
    }
  }
});
