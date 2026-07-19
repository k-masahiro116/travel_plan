(function () {
  const navToggle = document.querySelector(".nav__toggle");
  const navMenu = document.querySelector(".nav__menu");
  const navLinks = document.querySelectorAll(".nav__menu a");
  const tabs = document.querySelectorAll(".route-tabs__btn");
  const panels = document.querySelectorAll(".route-panel");

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

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const targetId = tab.getAttribute("aria-controls");
      const targetPanel = document.getElementById(targetId);

      tabs.forEach((item) => {
        const isActive = item === tab;
        item.classList.toggle("is-active", isActive);
        item.setAttribute("aria-selected", String(isActive));
        item.tabIndex = isActive ? 0 : -1;
      });

      panels.forEach((panel) => {
        const isActive = panel.id === targetId;
        panel.classList.toggle("is-active", isActive);
        panel.hidden = !isActive;
      });

      if (targetPanel) {
        targetPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    });

    tab.addEventListener("keydown", (event) => {
      const index = Array.from(tabs).indexOf(tab);
      let nextIndex = index;

      if (event.key === "ArrowRight" || event.key === "ArrowDown") {
        nextIndex = (index + 1) % tabs.length;
      } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
        nextIndex = (index - 1 + tabs.length) % tabs.length;
      } else {
        return;
      }

      event.preventDefault();
      tabs[nextIndex].click();
      tabs[nextIndex].focus();
    });
  });
})();
