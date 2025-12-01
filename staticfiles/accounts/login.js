function showModal(modalId) {
  document.getElementById('modalBackdrop').classList.add('show');
  document.getElementById(modalId).classList.add('show');
}

function closeModal(modalId) {
  document.getElementById('modalBackdrop').classList.remove('show');
  document.getElementById(modalId).classList.remove('show');
}

document.getElementById('modalBackdrop').addEventListener('click', function () {
  document.querySelectorAll('.modal.show').forEach(modal => {
    modal.classList.remove('show');
  });
  this.classList.remove('show');
});