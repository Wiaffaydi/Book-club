// Функция для плавной прокрутки
function smoothScroll(target) {
    const element = document.querySelector(target);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth'
        });
    }
}

// Обработчик для кнопок прокрутки
document.querySelectorAll('[data-scroll]').forEach(button => {
    button.addEventListener('click', (e) => {
        e.preventDefault();
        const target = button.getAttribute('data-scroll');
        smoothScroll(target);
    });
});

// Функция для отображения/скрытия мобильного меню
function toggleMobileMenu() {
    const menu = document.querySelector('.mobile-menu');
    if (menu) {
        menu.classList.toggle('active');
    }
}

// Обработчик для кнопки мобильного меню
const mobileMenuButton = document.querySelector('.mobile-menu-button');
if (mobileMenuButton) {
    mobileMenuButton.addEventListener('click', toggleMobileMenu);
}

// Функция для подтверждения действий
function confirmAction(message) {
    return confirm(message);
}

// Обработчик для кнопок с подтверждением
document.querySelectorAll('[data-confirm]').forEach(button => {
    button.addEventListener('click', (e) => {
        const message = button.getAttribute('data-confirm');
        if (!confirmAction(message)) {
            e.preventDefault();
        }
    });
}); 