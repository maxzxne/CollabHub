// Функции для управления авторизацией

function switchTab(tab) {
    const loginTab = document.getElementById('login-tab');
    const registerTab = document.getElementById('register-tab');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    
    if (tab === 'login') {
        loginTab.className = 'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all bg-white text-black shadow-sm';
        registerTab.className = 'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all text-gray-600 hover:text-black';
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
    } else {
        loginTab.className = 'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all text-gray-600 hover:text-black';
        registerTab.className = 'flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all bg-white text-black shadow-sm';
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
    }
}

function closeAuthOverlay() {
    // Не закрываем overlay, чтобы пользователь обязательно авторизовался
    // Можно добавить логику для временного скрытия
}

function showAuthOverlay() {
    window.location.href = '/'; // Redirect to home page, overlay will show
}

// Блокируем скролл страницы при активном overlay
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('auth-overlay')) {
        document.body.classList.add('overlay-active');
        
        // Предотвращаем закрытие overlay кликом вне формы
        document.getElementById('auth-overlay').addEventListener('click', function(e) {
            if (e.target === this) {
                // Не закрываем overlay
            }
        });
    }
});

// Восстанавливаем скролл при закрытии overlay (если будет реализовано)
function closeAuthOverlay() {
    document.body.classList.remove('overlay-active');
}
