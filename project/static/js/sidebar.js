// =========================
// Sidebar
// =========================


function toggleSidebar() {

    document
        .querySelector(".sidebar")
        .classList
        .toggle("show");

    document
        .querySelector(".sidebar-overlay")
        .classList
        .toggle("show");

}

function closeSidebar() {

    document
        .querySelector(".sidebar")
        .classList
        .remove("show");

    document
        .querySelector(".sidebar-overlay")
        .classList
        .remove("show");

}

// Close sidebar when a menu item is clicked on mobile
document.querySelectorAll(".sidebar a").forEach(link => {

    link.addEventListener("click", () => {

        if(window.innerWidth <= 768){

            closeSidebar();

        }

    });

});

// Close sidebar if screen becomes desktop
window.addEventListener("resize", () => {

    if(window.innerWidth > 768){

        closeSidebar();

    }

});
