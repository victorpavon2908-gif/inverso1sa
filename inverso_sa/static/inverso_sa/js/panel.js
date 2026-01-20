// Theme toggle functionality
function toggleTheme() {
    const isDarkMode = document.body.classList.toggle('dark-mode');
    const themeToggle = document.getElementById('themeToggle');

    // Update icon
    themeToggle.textContent = isDarkMode ? '☀️' : '🌙';

    // Save preference to localStorage
    localStorage.setItem('themeMode', isDarkMode ? 'dark' : 'light');
}

function initTheme() {
    const savedTheme = localStorage.getItem('themeMode');

    // Default to dark mode if no preference saved
    const isDarkMode = savedTheme ? (savedTheme === 'dark') : true;

    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        document.getElementById('themeToggle').textContent = '☀️';
    } else {
        document.body.classList.remove('dark-mode');
        document.getElementById('themeToggle').textContent = '🌙';
    }
}

// Call initTheme on page load
window.addEventListener('DOMContentLoaded', initTheme);


function showSection(sectionId, element) {
    // Hide all sections
    document.querySelectorAll('[id$="-section"]').forEach(section => {
        section.style.display = 'none';
    });

    // Show selected section
    document.getElementById(sectionId + '-section').style.display = 'block';

    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    element.classList.add('active');

    // Update header
    const titles = {
        'dashboard': 'Panel de Control',
        'usuarios': 'Gestión de Usuarios',
        'ordenes-trabajo': 'Órdenes de Trabajo',
        'clientes': 'Clientes',
        'tareas': 'Tareas'
    };

    const subtitles = {
        'dashboard': '¡Bienvenido! Aquí está un resumen de tu negocio',
        'usuarios': 'Administra los usuarios del sistema',
        'ordenes-trabajo': 'Gestiona las órdenes de trabajo',
        'clientes': 'Información de tus clientes',
        'tareas': 'Tus tareas pendientes'
    };

    document.getElementById('pageTitle').textContent = titles[sectionId] || 'Panel';
    document.getElementById('pageSubtitle').textContent = subtitles[sectionId] || '';
}





