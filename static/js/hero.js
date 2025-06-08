document.addEventListener('DOMContentLoaded', () => {
    const hero = document.querySelector('hero');
    let lastScrollTop = 0;

    // Function to handle scroll
    const handleScroll = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const heroHeight = hero.offsetHeight;
      const maxScroll = heroHeight * 0.8; // Fade out completely by 80% of hero height

      // Determine scroll direction
      const isScrollingDown = scrollTop > lastScrollTop;

      // Calculate opacity based on scroll position
      const opacity = Math.max(0, 1 - scrollTop / maxScroll);

      // Apply opacity based on scroll direction
      if (isScrollingDown) {
        // Fade out when scrolling down
        hero.style.opacity = opacity;
      } else {
        // Fade in when scrolling up, but only if hero is still in view
        if (scrollTop < heroHeight) {
          hero.style.opacity = opacity;
        }
      }

      lastScrollTop = scrollTop <= 0 ? 0 : scrollTop; // Update last scroll position
    };

    // Add scroll event listener
    window.addEventListener('scroll', handleScroll);

    // Initial opacity setting
    hero.style.transition = 'opacity 0.3s ease'; // Smooth transition for opacity
    hero.style.opacity = 1; // Start fully visible
  });