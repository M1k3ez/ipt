// flash.js
document.addEventListener("DOMContentLoaded", function() {
  function showFlashMessage(message, category) {
      const notification = document.createElement('ul');
      notification.className = `notification ${category}`;
      notification.innerHTML = `<li>${message}</li>`;

      document.body.appendChild(notification);

      notification.addEventListener('animationend', function() {
          notification.classList.add('hidden');
          setTimeout(() => notification.remove(), 1000); // Remove the element after it is hidden
      });
  }

  window.showFlashMessage = showFlashMessage; // Make it globally available
});
