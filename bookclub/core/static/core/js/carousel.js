document.addEventListener('DOMContentLoaded', function() {
    console.log('Carousel script loaded');
    
    const carousel = document.getElementById('bookCarousel');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    console.log('Carousel element:', carousel);
    console.log('Previous button:', prevBtn);
    console.log('Next button:', nextBtn);
    
    if (!carousel || !prevBtn || !nextBtn) {
        console.log('Some carousel elements are missing');
        return;
    }
    
    const items = carousel.querySelectorAll('.carousel-item');
    console.log('Number of carousel items:', items.length);
    
    if (items.length === 0) {
        console.log('No carousel items found');
        return;
    }

    // Константы для расчетов
    const ITEM_WIDTH = 300; // Ширина элемента
    const GAP = 32; // Отступ между элементами (2rem)
    const ITEM_TOTAL_WIDTH = ITEM_WIDTH + GAP;
    
    // Получаем ширину контейнера
    const containerWidth = carousel.parentElement.offsetWidth;
    console.log('Container width:', containerWidth);
    
    // Рассчитываем максимальное смещение
    const maxPosition = -(items.length * ITEM_TOTAL_WIDTH - containerWidth);
    console.log('Max position:', maxPosition);
    
    // Текущая позиция
    let position = 0;

    function updateCarousel() {
        // Ограничиваем позицию
        position = Math.max(Math.min(position, 0), maxPosition);
        
        // Применяем трансформацию
        carousel.style.transform = `translateX(${position}px)`;
        
        // Обновляем состояние кнопок
        prevBtn.disabled = position >= 0;
        nextBtn.disabled = position <= maxPosition;
        
        // Обновляем внешний вид кнопок
        prevBtn.style.opacity = position >= 0 ? '0.5' : '1';
        nextBtn.style.opacity = position <= maxPosition ? '0.5' : '1';
        
        console.log('Current position:', position);
    }
    
    // Функция для определения ширины прокрутки
    function getScrollStep() {
        if (window.innerWidth <= 600) {
            return ITEM_TOTAL_WIDTH; // Только 1 книга на мобильных
        } else {
            return ITEM_TOTAL_WIDTH * 3; // Как было для десктопа
        }
    }

    // Обработчики кнопок
    prevBtn.addEventListener('click', () => {
        console.log('Previous button clicked');
        position += getScrollStep();
        updateCarousel();
    });
    
    nextBtn.addEventListener('click', () => {
        console.log('Next button clicked');
        position -= getScrollStep();
        updateCarousel();
    });
    
    // Инициализация
    updateCarousel();
    
    // Обработка изменения размера окна
    window.addEventListener('resize', () => {
        console.log('Window resized');
        const newContainerWidth = carousel.parentElement.offsetWidth;
        const newMaxPosition = -(items.length * ITEM_TOTAL_WIDTH - newContainerWidth);
        
        // Корректируем позицию если нужно
        if (position < newMaxPosition) {
            position = newMaxPosition;
        }
        
        updateCarousel();
    });
});