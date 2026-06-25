// static/js/header-nav.js
(() => {
    'use strict';

    /**
     * HEADER NAVIGATION CONTROLLER
     * - User dropdown
     * - Active menu highlighting
     * - Loading overlay
     * - Smooth navigation
     * - SPA-safe initialization
     */

    class HeaderNavigation {
        constructor() {
            this.loadingOverlay = null;
            this.userMenuBtn = null;
            this.userDropdown = null;
        }

        /**
         * Khởi tạo toàn bộ navigation
         */
        init() {
            this.cacheElements();
            this.bindUserDropdown();
            this.setActiveMenu();
            this.bindNavigation();
            this.bindWindowEvents();

            console.log('Header navigation initialized successfully.');
        }

        /**
         * Cache DOM elements
         */
        cacheElements() {
            this.userMenuBtn = document.getElementById('userMenuBtn');
            this.userDropdown = document.getElementById('userDropdown');
        }

        /**
         * ==========================
         * USER DROPDOWN
         * ==========================
         */
        bindUserDropdown() {
            if (!this.userMenuBtn || !this.userDropdown) return;

            // Xóa event cũ nếu SPA load lại
            this.userMenuBtn.replaceWith(this.userMenuBtn.cloneNode(true));

            // Cập nhật lại reference
            this.userMenuBtn = document.getElementById('userMenuBtn');

            this.userMenuBtn.addEventListener('click', (event) => {
                event.stopPropagation();
                this.userDropdown.classList.toggle('show');
            });

            document.addEventListener('click', (event) => {
                if (!this.userDropdown.contains(event.target)) {
                    this.userDropdown.classList.remove('show');
                }
            });
        }

        /**
         * ==========================
         * ACTIVE MENU HIGHLIGHT
         * ==========================
         */
        setActiveMenu() {
            const currentPath = this.normalizePath(window.location.pathname);

            const links = document.querySelectorAll(
                '.nav-menu .nav-link, .dropdown-menu a'
            );

            let activeLink = null;
            let longestMatch = 0;

            links.forEach((link) => {
                const href = link.getAttribute('href');

                if (!href || href === '#' || href.startsWith('javascript:')) {
                    return;
                }

                const normalizedHref = this.normalizePath(href);

                // So khớp theo prefix dài nhất để xác định menu phù hợp nhất
                if (
                    currentPath.startsWith(normalizedHref) &&
                    normalizedHref.length > longestMatch
                ) {
                    longestMatch = normalizedHref.length;
                    activeLink = link;
                }
            });

            if (!activeLink) return;

            // Highlight link hiện tại
            activeLink.classList.add('active');

            // Nếu nằm trong dropdown, highlight menu cha
            const parentDropdown = activeLink.closest('.nav-item.dropdown');
            if (parentDropdown) {
                const parentLink = parentDropdown.querySelector(
                    ':scope > .nav-link'
                );

                if (parentLink) {
                    parentLink.classList.add('active');
                }
            }
        }

        /**
         * Chuẩn hóa path:
         * /abc/ => /abc
         */
        normalizePath(path) {
            if (!path) return '/';

            if (path.length > 1 && path.endsWith('/')) {
                return path.slice(0, -1);
            }

            return path;
        }

        /**
         * ==========================
         * LOADING OVERLAY
         * ==========================
         */
        createLoadingOverlay() {
            if (this.loadingOverlay) {
                return this.loadingOverlay;
            }

            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-spinner"></div>
            `;

            document.body.appendChild(overlay);

            this.loadingOverlay = overlay;
            return overlay;
        }

        showLoading() {
            const overlay = this.createLoadingOverlay();

            requestAnimationFrame(() => {
                overlay.classList.add('active');
            });
        }

        hideLoading() {
            if (this.loadingOverlay) {
                this.loadingOverlay.classList.remove('active');
            }
        }

        /**
         * ==========================
         * NAVIGATION HANDLING
         * ==========================
         */
        bindNavigation() {
            const links = document.querySelectorAll(
                '.nav-menu a, .user-dropdown a'
            );

            links.forEach((link) => {
                // Tránh bind nhiều lần
                if (link.dataset.navBound === 'true') return;
                link.dataset.navBound = 'true';

                const href = link.getAttribute('href');

                // Bỏ qua link không hợp lệ
                if (
                    !href ||
                    href === '#' ||
                    href.startsWith('javascript:') ||
                    href.startsWith('mailto:') ||
                    href.startsWith('tel:') ||
                    link.hasAttribute('target') ||
                    href === '/logout/'
                ) {
                    return;
                }

                link.addEventListener('click', (event) => {
                    // Chỉ xử lý click chuột trái thông thường
                    if (
                        event.ctrlKey ||
                        event.shiftKey ||
                        event.altKey ||
                        event.metaKey ||
                        event.button !== 0
                    ) {
                        return;
                    }

                    event.preventDefault();
                    this.showLoading();

                    // Delay nhỏ để animation hiển thị
                    setTimeout(() => {
                        window.location.assign(href);
                    }, 120);
                });
            });
        }

        /**
         * ==========================
         * WINDOW EVENTS
         * ==========================
         */
        bindWindowEvents() {
            // Khi trang tải xong -> ẩn loading
            window.addEventListener('load', () => {
                setTimeout(() => this.hideLoading(), 250);
            });

            // Khi quay lại bằng Back/Forward Cache
            window.addEventListener('pageshow', () => {
                this.hideLoading();
            });
        }
    }

    /**
     * Khởi tạo an toàn cho cả:
     * - Page load thông thường
     * - Django templates
     * - SPA content replacement
     */
    function initializeHeaderNavigation() {
        const navigation = new HeaderNavigation();
        navigation.init();

        // Expose để có thể gọi lại khi SPA load nội dung mới
        window.headerNavigation = navigation;
    }

    if (document.readyState === 'loading') {
        document.addEventListener(
            'DOMContentLoaded',
            initializeHeaderNavigation,
            { once: true }
        );
    } else {
        initializeHeaderNavigation();
    }
})();