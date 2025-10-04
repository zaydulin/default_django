document.addEventListener('DOMContentLoaded', function() {
            const sidebar = document.getElementById('sidebar');
            const content = document.getElementById('content');
            const menuToggle = document.getElementById('menuToggle');
            const navLinks = document.querySelectorAll('.sidebar .nav-link');
            const submenuItems = document.querySelectorAll('.nav-item.has-submenu > .nav-link');

            // Устанавливаем начальное состояние переключателя
            menuToggle.checked = true;

            // Функция для переключения боковой панели
            function toggleSidebarState() {
                const isOpen = menuToggle.checked;
                sidebar.classList.toggle('collapsed', !isOpen);
                content.classList.toggle('expanded', !isOpen);
            }

            // Обработчик события для переключателя
            menuToggle.addEventListener('change', toggleSidebarState);

            // Обработчики для подменю
            submenuItems.forEach(item => {
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    const parent = this.parentElement;

                    // Закрываем другие открытые подменю
                    document.querySelectorAll('.nav-item.has-submenu.active').forEach(activeItem => {
                        if (activeItem !== parent) {
                            activeItem.classList.remove('active');
                        }
                    });

                    parent.classList.toggle('active');
                });
            });

            // Обработчики для активных ссылок
            navLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    if (!this.parentElement.classList.contains('has-submenu')) {
                        // Удаляем активный класс у всех ссылок
                        navLinks.forEach(l => l.classList.remove('active'));
                        // Добавляем активный класс к текущей ссылке
                        this.classList.add('active');
                    }

                    // Закрываем боковую панель на мобильных устройствах после выбора пункта
                    if (window.innerWidth <= 768) {
                        menuToggle.checked = false;
                        toggleSidebarState();
                    }
                });
            });

            // Обработка изменения размера окна
            window.addEventListener('resize', function() {
                if (window.innerWidth <= 768) {
                    // На мобильных устройствах боковая панель по умолчанию скрыта
                    menuToggle.checked = false;
                    toggleSidebarState();
                } else {
                    // На больших экранах боковая панель по умолчанию открыта
                    menuToggle.checked = true;
                    toggleSidebarState();
                }
            });

            // Инициализация состояния на основе размера экрана
            if (window.innerWidth <= 768) {
                menuToggle.checked = false;
                toggleSidebarState();
            }
        });