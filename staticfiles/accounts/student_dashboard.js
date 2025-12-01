
function showTab(event, tabName) {
  // Hide all tab contents
  const contents = document.querySelectorAll('.tab-content');
  contents.forEach(content => content.classList.remove('active'));

  // Remove active class from all buttons
  const buttons = document.querySelectorAll('.tab-button');
  buttons.forEach(button => button.classList.remove('active'));

  // Show selected tab
  document.getElementById(tabName).classList.add('active');
  event.target.classList.add('active');
}

function handleBrowseFormSubmit(event) {
  event.preventDefault();

  const search = document.getElementById('browseSearch').value;
  const status = document.getElementById('browseStatus').value;

  // Build query string
  let queryString = '';
  if (search || status !== 'all') {
    queryString = '?tab=browse';
    if (search) {
      queryString += '&search=' + encodeURIComponent(search);
    }
    if (status !== 'all') {
      queryString += '&status=' + encodeURIComponent(status);
    }
  } else {
    queryString = '?tab=browse';
  }

  // Navigate with query string
  window.location.href = window.location.pathname + queryString;
  return false;
}

function resetBrowseFilter(event) {
  event.preventDefault();
  document.getElementById('browseSearch').value = '';
  document.getElementById('browseStatus').value = 'all';
  window.location.href = window.location.pathname + '?tab=browse';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
  // Check if we should show browse tab (from URL parameter)
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('tab') && urlParams.get('tab') === 'browse') {
    // Activate browse tab
    const browseTab = document.querySelector('button[onclick*="browse"]');
    if (browseTab) {
      browseTab.click();
    }
  }

  // Auto-submit form when filter changes
  const filterSelect = document.getElementById('browseStatus');
  if (filterSelect) {
    filterSelect.addEventListener('change', function () {
      document.getElementById('browseBooksForm').dispatchEvent(new Event('submit'));
    });
  }
});