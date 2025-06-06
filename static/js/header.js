(() => {
    // Smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", (e) => {
        e.preventDefault();
        const target = document.querySelector(anchor.getAttribute("href"));
        target?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });

    // Header scroll effect
    const header = document.querySelector(".header");
    let lastY = 0;

    const updateHeader = () => {
      const currentY = window.scrollY;
      const opacity = currentY > 100 ? 0.95 : 0.9;
      const borderOpacity = currentY > 100 ? 0.2 : 0.1;

      header.style.background = `rgba(26, 26, 46, ${opacity})`;
      header.style.borderBottomColor = `rgba(255, 255, 255, ${borderOpacity})`;
      lastY = currentY;
    };

    let ticking = false;
    window.addEventListener("scroll", () => {
      if (!ticking) {
        requestAnimationFrame(updateHeader);
        ticking = true;
        setTimeout(() => (ticking = false), 16);
      }
    });
  })();