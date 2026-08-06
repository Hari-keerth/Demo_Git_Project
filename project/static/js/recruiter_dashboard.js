document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.querySelector('.recruiter-sidebar');
    const mainContent = document.querySelector('.main');
    const toggleBtn = document.getElementById('sidebar-toggle-btn');

    if (toggleBtn && sidebar && mainContent) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('sidebar-collapsed');
            
            // Store state in localStorage so preference persists across page reloads
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebar_collapsed', isCollapsed);
        });

        // Restore saved preference
        if (localStorage.getItem('sidebar_collapsed') === 'true') {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('sidebar-collapsed');
        }
    }
});