// Функции для валидации форм

function initDateValidation() {
    const deadlineInput = document.getElementById('deadline');
    if (!deadlineInput) return;
    
    const dateError = document.getElementById('date-error');
    const form = deadlineInput.closest('form');
    const submitButton = form ? form.querySelector('button[type="submit"]') : null;
    
    // Устанавливаем минимальную дату (сегодня) и максимальную дату (2099 год)
    const today = new Date().toISOString().split('T')[0];
    const maxDateStr = '2099-12-31';
    
    deadlineInput.setAttribute('min', today);
    deadlineInput.setAttribute('max', maxDateStr);
    
    function validateDate() {
        const selectedDate = deadlineInput.value;
        const today = new Date().toISOString().split('T')[0];
        
        if (selectedDate && (selectedDate < today || selectedDate > maxDateStr)) {
            if (dateError) {
                dateError.classList.remove('hidden');
                if (selectedDate < today) {
                    dateError.textContent = 'Дата не может быть в прошлом';
                } else {
                    dateError.textContent = 'Дата не может быть позже 2099 года';
                }
            }
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.classList.add('opacity-50', 'cursor-not-allowed');
            }
            return false;
        } else {
            if (dateError) {
                dateError.classList.add('hidden');
            }
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.classList.remove('opacity-50', 'cursor-not-allowed');
            }
            return true;
        }
    }
    
    // Валидация при изменении даты
    deadlineInput.addEventListener('change', validateDate);
    
    // Валидация при отправке формы
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateDate()) {
                e.preventDefault();
                deadlineInput.focus();
            }
        });
    }
    
    // Первоначальная валидация
    validateDate();
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initDateValidation();
});
