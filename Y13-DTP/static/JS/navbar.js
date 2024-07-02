let lastScrollTop = 0;
window.addEventListener("scroll", function() {
  let navbar = document.querySelector(".navbar"); // Get the navbar element
  let scrollTop = window.pageYOffset || document.documentElement.scrollTop; // Get current scroll position
  // If scrolling down, add 'hidden' class to navbar, otherwise remove it
  if (scrollTop > lastScrollTop) {
    navbar.classList.add("hidden");
  } else {
    navbar.classList.remove("hidden");
  }

  lastScrollTop = scrollTop; // Update last scroll position
});
