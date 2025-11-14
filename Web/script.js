// --- LÓGICA DA ANIMAÇÃO SPLASH SCREEN ---
document.addEventListener('DOMContentLoaded', () => {
    // Apenas executa a animação de splash na página principal (index.html)
    const splashScreen = document.getElementById('splash-screen');
    if (splashScreen) {
        const mainContent = document.getElementById('main-content');
        const truck = document.querySelector('.truck');
        const wheels = document.querySelector('.wheels');
        const logoLetters = document.querySelectorAll('.logo-letter');
        const lastLetter = logoLetters[logoLetters.length - 1];
        
        document.body.classList.add('splash-active');

        setTimeout(() => {
            truck.classList.add('drive-in');
            wheels.classList.add('drive-in');
        }, 100);

        truck.addEventListener('animationend', (event) => {
            if (event.animationName === 'driveInAndStop') {
                logoLetters.forEach((letter, index) => {
                    setTimeout(() => {
                        letter.style.animation = `letterDrop 0.5s forwards, letterBounce 1s ease-out 0.5s forwards`;
                    }, index * 80);
                });
            }
        });

        lastLetter.addEventListener('animationend', (event) => {
            if (event.animationName === 'letterBounce') {
                setTimeout(() => {
                    splashScreen.style.opacity = 0;
                    splashScreen.addEventListener('transitionend', () => {
                        splashScreen.style.display = 'none';
                        mainContent.style.visibility = 'visible';
                        document.body.classList.remove('splash-active');
                        document.body.style.overflow = 'auto';
                        initializeLandingPageScripts();
                    }, { once: true });
                }, 800);
            }
        });
    } else {
        // Se não for a página principal, apenas inicializa os scripts normais
        initializeLandingPageScripts();
    }
});


// --- LÓGICA DA LANDING PAGE ---
function initializeLandingPageScripts() {
    // Animação de Scroll
    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) entry.target.classList.add('visible');
        });
    }, { threshold: 0.1 });
    document.querySelectorAll('.scroll-animation').forEach(el => scrollObserver.observe(el));

    // Animação de Contagem dos Números
    const statsObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = +counter.getAttribute('data-target');
                const duration = 1500;
                const stepTime = Math.abs(Math.floor(duration / target));
                let current = 0;
                const timer = setInterval(() => {
                    current += 1;
                    counter.innerText = current + '%';
                    if (current >= target) clearInterval(timer);
                }, stepTime);
                observer.unobserve(counter);
            }
        });
    }, { threshold: 0.5 });
    document.querySelectorAll('.stat-number').forEach(stat => statsObserver.observe(stat));

    // Funcionalidade do Acordeão FAQ
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        question.addEventListener('click', () => {
            const currentlyActive = document.querySelector('.faq-item.active');
            if (currentlyActive && currentlyActive !== item) {
                currentlyActive.classList.remove('active');
            }
            item.classList.toggle('active');
        });
    });

    // Botão Voltar ao Topo
    const backToTopButton = document.querySelector('.back-to-top');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTopButton.classList.add('visible');
        } else {
            backToTopButton.classList.remove('visible');
        }
    });

    // A LÓGICA DAS ABAS FOI REMOVIDA
}