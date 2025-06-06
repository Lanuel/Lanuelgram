 // Alternative JavaScript implementation for better browser support
  document.addEventListener("DOMContentLoaded", function () {
    const topButton = document.querySelector("#nav-top .button-dark");
    if (topButton) {
      topButton.addEventListener("click", function () {
        window.scrollTo({
          top: 0,
          behavior: "smooth",
        });
      });
    }

    // Optional: Show/hide button based on scroll position
    window.addEventListener("scroll", function () {
      if (window.pageYOffset > 500) {
        topButton.style.display = "block";
      } else {
        topButton.style.display = "none";
      }
    });
  });