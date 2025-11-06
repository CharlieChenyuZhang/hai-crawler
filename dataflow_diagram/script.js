// Add interactivity to the visualization

document.addEventListener('DOMContentLoaded', function() {
    // Animate stat numbers on scroll
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const statNumber = entry.target.querySelector('.stat-number');
                if (statNumber && !statNumber.classList.contains('animated')) {
                    animateNumber(statNumber);
                    statNumber.classList.add('animated');
                }
            }
        });
    }, observerOptions);

    document.querySelectorAll('.stat-card').forEach(card => {
        observer.observe(card);
    });

    // Animate topic bars on scroll
    const topicObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('animated')) {
                const bar = entry.target.querySelector('.topic-bar-fill');
                if (bar) {
                    const width = bar.style.width;
                    bar.style.width = '0%';
                    setTimeout(() => {
                        bar.style.width = width;
                    }, 100);
                    entry.target.classList.add('animated');
                }
            }
        });
    }, observerOptions);

    document.querySelectorAll('.topic-bar').forEach(bar => {
        topicObserver.observe(bar);
    });

    // Add click interactions to pipeline stages
    document.querySelectorAll('.stage').forEach(stage => {
        stage.addEventListener('click', function() {
            const stageNum = this.dataset.stage;
            highlightStage(stageNum);
        });
    });

    // Add hover effects with ripple
    document.querySelectorAll('.finding-card, .stat-card').forEach(card => {
        card.addEventListener('mouseenter', function(e) {
            createRipple(this, e);
        });
    });
});

function animateNumber(element) {
    const text = element.textContent;
    const numbers = text.match(/\d+/g);
    
    if (!numbers) return;
    
    const targetNumber = parseInt(numbers[0].replace(/,/g, ''));
    const suffix = text.replace(/[\d,]+/g, '').trim();
    const duration = 1500;
    const steps = 60;
    const increment = targetNumber / steps;
    let current = 0;
    
    element.textContent = '0' + suffix;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= targetNumber) {
            element.textContent = formatNumber(targetNumber) + suffix;
            clearInterval(timer);
        } else {
            element.textContent = formatNumber(Math.floor(current)) + suffix;
        }
    }, duration / steps);
}

function formatNumber(num) {
    if (num >= 1000) {
        return num.toLocaleString();
    }
    return num.toString();
}

function highlightStage(stageNum) {
    // Remove previous highlights
    document.querySelectorAll('.stage').forEach(s => {
        s.style.border = '';
    });
    
    // Highlight selected stage
    const selectedStage = document.querySelector(`[data-stage="${stageNum}"]`);
    if (selectedStage) {
        selectedStage.style.border = '3px solid #fbbf24';
        selectedStage.style.boxShadow = '0 0 20px rgba(251, 191, 36, 0.5)';
        
        // Reset after 2 seconds
        setTimeout(() => {
            selectedStage.style.border = '';
            selectedStage.style.boxShadow = '';
        }, 2000);
    }
}

function createRipple(element, event) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    // Center the ripple if clientX/Y not available
    const x = (event && event.clientX ? event.clientX - rect.left : rect.width / 2) - size / 2;
    const y = (event && event.clientY ? event.clientY - rect.top : rect.height / 2) - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Add smooth scrolling for better UX
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading animation
window.addEventListener('load', function() {
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
});
