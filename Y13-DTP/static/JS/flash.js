document.addEventListener("DOMContentLoaded", function() {
    const notification = document.querySelector('.notification');
    notification.addEventListener('animationend', function() {
      notification.classList.add('hidden');
    });
  });