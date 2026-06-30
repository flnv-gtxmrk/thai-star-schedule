// ─────────────────────────────────────────────
// StarTrack — Main JavaScript
// ─────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    initTheme();
    initNav();
    initDropdown();
    initFlash();
    initPromo();
    initSmoothScroll();
    initLangSwitcher();
});

// ─── Starfield Particle System ───
function initParticles() {
    const canvas = document.createElement('canvas');
    canvas.id = 'particleCanvas';
    document.body.prepend(canvas);
    const ctx = canvas.getContext('2d');

    let w, h, stars;
    const count = 80;

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }

    function create() {
        resize();
        stars = Array.from({ length: count }, () => ({
            x: Math.random() * w,
            y: Math.random() * h,
            r: Math.random() * 1.8 + 0.4,
            baseAlpha: Math.random() * 0.5 + 0.15,
            alpha: 0,
            twinkleSpeed: Math.random() * 0.015 + 0.005,
            twinkleOffset: Math.random() * Math.PI * 2
        }));
    }

    function draw() {
        ctx.clearRect(0, 0, w, h);
        const t = Date.now() * 0.001;

        stars.forEach(s => {
            // Twinkling: oscillate alpha using sin
            s.alpha = s.baseAlpha * (0.5 + 0.5 * Math.sin(t * s.twinkleSpeed * 60 + s.twinkleOffset));

            // Draw glow
            const grd = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 3);
            grd.addColorStop(0, `rgba(255,255,255,${s.alpha})`);
            grd.addColorStop(0.3, `rgba(180,200,255,${s.alpha * 0.6})`);
            grd.addColorStop(1, 'rgba(180,200,255,0)');

            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r * 3, 0, Math.PI * 2);
            ctx.fillStyle = grd;
            ctx.fill();

            // Bright core
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255,255,255,${s.alpha * 1.3})`;
            ctx.fill();
        });

        requestAnimationFrame(draw);
    }

    window.addEventListener('resize', () => { resize(); create(); });
    create();
    draw();
}

// ─── Theme Toggle ───
function initTheme() {
    const btn = document.getElementById('themeToggle');
    const saved = localStorage.getItem('theme') || 'dark';
    if (saved === 'light') document.documentElement.setAttribute('data-theme', 'light');
    updateIcon(btn);

    if (btn) {
        btn.addEventListener('click', () => {
            const isLight = document.documentElement.hasAttribute('data-theme');
            if (isLight) {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'dark');
            } else {
                document.documentElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
            }
            updateIcon(btn);
        });
    }
}

function updateIcon(btn) {
    const icon = btn?.querySelector('i');
    if (icon) {
        icon.className = document.documentElement.hasAttribute('data-theme') ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// ─── Mobile Nav ───
function initNav() {
    const btn = document.getElementById('mobileMenuBtn');
    const links = document.getElementById('navLinks');
    if (btn && links) {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            e.preventDefault();
            links.classList.toggle('show');
        });
        // Close when clicking a link
        links.querySelectorAll('.nav-link').forEach(l => {
            l.addEventListener('click', () => links.classList.remove('show'));
        });
        // Close when clicking outside
        document.addEventListener('click', e => {
            if (!links.contains(e.target) && e.target !== btn) {
                links.classList.remove('show');
            }
        });
    }
}

// ─── User Dropdown ───
function initDropdown() {
    const btn = document.getElementById('userBtn');
    const menu = document.getElementById('dropdownMenu');
    if (btn && menu) {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            e.preventDefault();
            menu.classList.toggle('show');
        });
        // Prevent clicks inside menu from closing it
        menu.addEventListener('click', e => {
            e.stopPropagation();
        });
        // Close when clicking anywhere else
        document.addEventListener('click', () => {
            menu.classList.remove('show');
        });
    }
}

// ─── Flash Messages ───
function initFlash() {
    document.querySelectorAll('.flash-message').forEach(msg => {
        const close = msg.querySelector('.flash-close');
        if (close) close.addEventListener('click', () => { msg.style.opacity = '0'; setTimeout(() => msg.remove(), 200); });
        setTimeout(() => { if (msg.parentNode) { msg.style.opacity = '0'; setTimeout(() => msg.remove(), 200); } }, 4000);
    });
}

// ─── Promo Banner ───
function initPromo() {
    const banner = document.getElementById('promoBanner');
    const close = document.getElementById('promoClose');
    if (banner && close) {
        const t = setTimeout(() => { if (!sessionStorage.getItem('promo')) banner.classList.add('show'); }, 5000);
        close.addEventListener('click', () => { banner.classList.remove('show'); clearTimeout(t); sessionStorage.setItem('promo', '1'); });
    }
}

// ─── Smooth Scroll ───
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', e => {
            const t = document.querySelector(a.getAttribute('href'));
            if (t) { e.preventDefault(); t.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
        });
    });
}

// ─── Language Switcher ───
function initLangSwitcher() {
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const lang = btn.getAttribute('data-lang');
            window.location.href = '/lang/' + lang;
        });
    });
}
