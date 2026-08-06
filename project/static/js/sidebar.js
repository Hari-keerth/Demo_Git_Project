// ==========================================================
// CareerGrowza Sidebar
// ==========================================================

const sidebar = document.querySelector(".sidebar");
const overlay = document.querySelector(".sidebar-overlay");
const menuButton = document.querySelector(".menu-toggle");

// ==========================================================
// Toggle Sidebar (Mobile Only)
// ==========================================================

function toggleSidebar() {

    if (window.innerWidth <= 768) {

        sidebar.classList.toggle("show");
        overlay.classList.toggle("show");

    }

}

// ==========================================================
// Close Sidebar
// ==========================================================

function closeSidebar() {

    sidebar.classList.remove("show");
    overlay.classList.remove("show");

}

// ==========================================================
// Menu Button
// ==========================================================

if (menuButton) {

    menuButton.addEventListener("click", toggleSidebar);

}

// ==========================================================
// Overlay Click
// ==========================================================

if (overlay) {

    overlay.addEventListener("click", closeSidebar);

}

// ==========================================================
// Close Sidebar after clicking a link (Mobile)
// ==========================================================

document.querySelectorAll(".sidebar a").forEach(link => {

    link.addEventListener("click", () => {

        if (window.innerWidth <= 768) {

            closeSidebar();

        }

    });

});

// ==========================================================
// ESC Key
// ==========================================================

document.addEventListener("keydown", (event) => {

    if (event.key === "Escape") {

        closeSidebar();

    }

});

// ==========================================================
// Window Resize
// ==========================================================

window.addEventListener("resize", () => {

    if (window.innerWidth > 768) {

        closeSidebar();

    }

});

// ==========================================================
// Initial State
// ==========================================================

window.addEventListener("load", () => {

    closeSidebar();

});