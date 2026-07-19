(function () {
  const navToggle = document.querySelector(".nav__toggle");
  const navMenu = document.querySelector(".nav__menu");
  const navLinks = document.querySelectorAll(".nav__menu a");

  if (!navToggle || !navMenu) return;

  navToggle.addEventListener("click", () => {
    const isOpen = navMenu.classList.toggle("is-open");
    navToggle.setAttribute("aria-expanded", String(isOpen));
  });

  navLinks.forEach((link) => {
    link.addEventListener("click", () => {
      navMenu.classList.remove("is-open");
      navToggle.setAttribute("aria-expanded", "false");
    });
  });

  document.addEventListener("click", (event) => {
    if (
      !navMenu.classList.contains("is-open") ||
      navMenu.contains(event.target) ||
      navToggle.contains(event.target)
    ) {
      return;
    }

    navMenu.classList.remove("is-open");
    navToggle.setAttribute("aria-expanded", "false");
  });
})();
