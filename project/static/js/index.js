/* ==========================================================================
   CareerGrowza — Landing Page Behaviour
   Sections: mobile nav, scroll header, reveal-on-scroll, growth-ring draw,
   stat counters, smooth-scroll nav highlighting.
   (Behavior unchanged from original — nav stays a top bar with a
   slide-in mobile panel, not a persistent sidebar.)
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {

  /* ---------- Mobile nav toggle ---------- */
  var menuToggle = document.getElementById("menuToggle");
  var navLinks = document.getElementById("navLinks");
  var navOverlay = document.getElementById("navOverlay");

  function closeNav() {
    navLinks.classList.remove("show");
    navOverlay.classList.remove("show");
    menuToggle.setAttribute("aria-expanded", "false");
  }

  function toggleNav() {
    var isOpen = navLinks.classList.toggle("show");
    navOverlay.classList.toggle("show", isOpen);
    menuToggle.setAttribute("aria-expanded", String(isOpen));
  }

  if (menuToggle) {
    menuToggle.addEventListener("click", toggleNav);
    navOverlay.addEventListener("click", closeNav);

    navLinks.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", closeNav);
    });
  }

  /* ---------- Header shadow on scroll ---------- */
  var header = document.getElementById("siteHeader");

  function updateHeaderState() {
    if (window.scrollY > 12) {
      header.style.borderBottomColor = "rgba(99, 102, 241, 0.25)";
      header.style.boxShadow = "0 8px 30px rgba(80, 90, 180, 0.10)";
    } else {
      header.style.borderBottomColor = "";
      header.style.boxShadow = "";
    }
  }

  window.addEventListener("scroll", updateHeaderState, { passive: true });
  updateHeaderState();

  /* ---------- Reveal-on-scroll ---------- */
  var revealItems = document.querySelectorAll(".reveal");

  var revealObserver = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.2 }
  );

  revealItems.forEach(function (item) {
    revealObserver.observe(item);
  });

  /* ---------- Growth-ring draw-in ---------- */
  var growthRings = document.getElementById("growthRings");

  if (growthRings) {
    var ringObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("in-view");
            ringObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.3 }
    );

    ringObserver.observe(growthRings);
  }

  /* ---------- Stat counters ---------- */
  var statNumbers = document.querySelectorAll(".stat-number");

  function animateCount(el) {
    var target = parseInt(el.getAttribute("data-count"), 10) || 0;
    var suffix = el.getAttribute("data-suffix") || "";
    var duration = 1400;
    var start = null;

    function step(timestamp) {
      if (start === null) start = timestamp;
      var progress = Math.min((timestamp - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var value = Math.floor(eased * target);
      el.textContent = value.toLocaleString() + suffix;

      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        el.textContent = target.toLocaleString() + suffix;
      }
    }

    requestAnimationFrame(step);
  }

  var statsObserver = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCount(entry.target);
          statsObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.5 }
  );

  statNumbers.forEach(function (el) {
    statsObserver.observe(el);
  });

  /* ---------- Smooth scroll for in-page nav links ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener("click", function (event) {
      var targetId = link.getAttribute("href");
      if (targetId.length > 1) {
        var targetEl = document.querySelector(targetId);
        if (targetEl) {
          event.preventDefault();
          targetEl.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }
    });
  });

});