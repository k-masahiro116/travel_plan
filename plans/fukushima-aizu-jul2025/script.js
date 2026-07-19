(function () {
  const navToggle = document.querySelector(".nav__toggle");
  const navMenu = document.querySelector(".nav__menu");
  const navLinks = document.querySelectorAll(".nav__menu a");

  if (navToggle && navMenu) {
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
  }

  document.querySelectorAll(".route-tabs").forEach((tablist) => {
    const tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));

    function activateTab(tab) {
      tabs.forEach((item) => {
        const isActive = item === tab;
        item.classList.toggle("is-active", isActive);
        item.setAttribute("aria-selected", String(isActive));
        item.tabIndex = isActive ? 0 : -1;

        const panel = document.getElementById(item.getAttribute("aria-controls"));
        if (!panel) return;
        panel.classList.toggle("is-active", isActive);
        panel.hidden = !isActive;
      });
    }

    const defaultTab =
      tabs.find((tab) => tab.classList.contains("is-active")) || tabs[0];
    if (defaultTab) activateTab(defaultTab);

    tabs.forEach((tab) => {
      tab.addEventListener("click", () => activateTab(tab));
      tab.addEventListener("keydown", (event) => {
        const index = tabs.indexOf(tab);
        let next = index;
        if (event.key === "ArrowRight" || event.key === "ArrowDown") {
          next = (index + 1) % tabs.length;
        } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
          next = (index - 1 + tabs.length) % tabs.length;
        } else return;
        event.preventDefault();
        tabs[next].click();
        tabs[next].focus();
      });
    });
  });
})();
