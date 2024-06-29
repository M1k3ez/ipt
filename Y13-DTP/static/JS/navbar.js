let lastScrollTop = 0;
window.addEventListener("scroll", function() {
  let navbar = document.querySelector(".navbar");
  let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  if (scrollTop > lastScrollTop) {
    navbar.classList.add("hidden");
  } else {
    navbar.classList.remove("hidden");
  }
  lastScrollTop = scrollTop;
});
