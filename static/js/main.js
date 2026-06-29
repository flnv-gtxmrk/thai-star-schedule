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

// ─── Particle System ───
function initParticles() {
    const canvas = document.createElement('canvas');
    canvas.id = 'particleCanvas';
    document.body.prepend(canvas);
    const ctx = canvas.getContext('2d');

    let w, h, particles;
    const count = 42;
    const maxDist = 110;

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }

    function create() {
        resize();
        particles = Array.from({ length: count }, () => ({
            x: Math.random() * w,
            y: Math.random() * h,
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4,
            r: Math.random() * 1.5 + 0.5,
            o: Math.random() * 0.4 + 0.2
        }));
    }

    function draw() {
        ctx.clearRect(0, 0, w, h);
        const isDark = !document.documentElement.hasAttribute('data-theme');
        const c = isDark ? '79,140,255' : '59,123,247';

        particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < 0) p.x = w;
            if (p.x > w) p.x = 0;
            if (p.y < 0) p.y = h;
            if (p.y > h) p.y = 0;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${c},${p.o})`;
            ctx.fill();
        });

        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const d = Math.sqrt(dx * dx + dy * dy);
                if (d < maxDist) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(${c},${(1 - d / maxDist) * 0.12})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }

        requestAnimationFrame(draw);
    }

    window.addEventListener('resize', resize);
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
        btn.addEventListener('click', () => links.classList.toggle('show'));
        links.querySelectorAll('.nav-link').forEach(l => l.addEventListener('click', () => links.classList.remove('show')));
    }
}

// ─── User Dropdown ───
function initDropdown() {
    const btn = document.getElementById('userBtn');
    const menu = document.getElementById('dropdownMenu');
    if (btn && menu) {
        btn.addEventListener('click', e => { e.stopPropagation(); menu.classList.toggle('show'); });
        document.addEventListener('click', () => menu.classList.remove('show'));
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
