// Neural Glass Theme JavaScript
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize all neural effects
    initializeNeuralEffects();
    initializeCardAnimations();
    initializeFormEffects();
    initializePageTransitions();
    initializeStatCounters();
    
    // Particle background effect
    createParticleBackground();
});

// Initialize neural effects
function initializeNeuralEffects() {
    // Add glow effect to buttons on hover
    const buttons = document.querySelectorAll('.btn-neural, .btn-neon');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.05)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Add ripple effect to buttons
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            createRippleEffect(e, this);
        });
    });
}

// Create ripple effect
function createRippleEffect(event, element) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    // Add ripple styles
    ripple.style.position = 'absolute';
    ripple.style.borderRadius = '50%';
    ripple.style.background = 'rgba(255, 255, 255, 0.6)';
    ripple.style.transform = 'scale(0)';
    ripple.style.animation = 'ripple 0.6s linear';
    ripple.style.pointerEvents = 'none';
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Add ripple animation to CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize card animations
function initializeCardAnimations() {
    const cards = document.querySelectorAll('.neural-card, .stat-card');
    
    // Intersection Observer for scroll animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });
    
    cards.forEach(card => {
        // Initial state for animation
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.6s ease';
        
        observer.observe(card);
        
        // Add hover effects
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Initialize form effects
function initializeFormEffects() {
    const inputs = document.querySelectorAll('.form-control-neural');
    
    inputs.forEach(input => {
        // Floating label effect
        const label = input.previousElementSibling;
        
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
            if (label && label.classList.contains('form-label')) {
                label.style.transform = 'translateY(-25px) scale(0.8)';
                label.style.color = 'var(--neon-blue)';
            }
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
                if (label && label.classList.contains('form-label')) {
                    label.style.transform = 'translateY(0) scale(1)';
                    label.style.color = '#ffffff';
                }
            }
        });
        
        // Check if input has value on load
        if (input.value) {
            input.parentElement.classList.add('focused');
            if (label && label.classList.contains('form-label')) {
                label.style.transform = 'translateY(-25px) scale(0.8)';
                label.style.color = 'var(--neon-blue)';
            }
        }
    });
}

// Initialize page transitions
function initializePageTransitions() {
    // Add page enter animation
    document.body.classList.add('page-enter');
    setTimeout(() => {
        document.body.classList.add('page-enter-active');
    }, 100);
    
    // Smooth scroll for anchor links
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
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
}

// Initialize stat counters (temporarily disabled animation)
function initializeStatCounters() {
    // Temporarily disable animation to debug the issue
    console.log('Stat counters initialized - animation disabled for debugging');
    return;
    
    const statNumbers = document.querySelectorAll('.stat-number');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const text = target.textContent;
                
                // Extract numeric value from text (handle currency symbols)
                const numericValue = text.replace(/[^\d]/g, '');
                const finalValue = parseInt(numericValue);
                
                // Only animate if we have a valid number
                if (!isNaN(finalValue) && finalValue > 0) {
                    const hasCurrency = text.includes('₹');
                    animateCounter(target, 0, finalValue, 2000, hasCurrency);
                }
                observer.unobserve(target);
            }
        });
    });
    
    statNumbers.forEach(stat => observer.observe(stat));
}

// Animate counter
function animateCounter(element, start, end, duration, hasCurrency = false) {
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + (end - start) * easeOut);
        
        // Format the number with currency if needed
        const formattedNumber = hasCurrency ? `₹${current.toLocaleString()}` : current.toLocaleString();
        element.textContent = formattedNumber;
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            const finalFormatted = hasCurrency ? `₹${end.toLocaleString()}` : end.toLocaleString();
            element.textContent = finalFormatted;
        }
    }
    
    requestAnimationFrame(updateCounter);
}

// Create particle background
function createParticleBackground() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '-2';
    canvas.style.opacity = '0.3';
    
    document.body.appendChild(canvas);
    
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    
    const particles = [];
    const particleCount = 50;
    
    // Create particles
    for (let i = 0; i < particleCount; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            size: Math.random() * 2 + 1,
            opacity: Math.random() * 0.5 + 0.2
        });
    }
    
    function animateParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            // Update position
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            // Wrap around edges
            if (particle.x < 0) particle.x = canvas.width;
            if (particle.x > canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = canvas.height;
            if (particle.y > canvas.height) particle.y = 0;
            
            // Draw particle
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 245, 255, ${particle.opacity})`;
            ctx.fill();
            
            // Draw connections
            particles.forEach(otherParticle => {
                const dx = particle.x - otherParticle.x;
                const dy = particle.y - otherParticle.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 100) {
                    ctx.beginPath();
                    ctx.moveTo(particle.x, particle.y);
                    ctx.lineTo(otherParticle.x, otherParticle.y);
                    ctx.strokeStyle = `rgba(0, 245, 255, ${0.1 * (1 - distance / 100)})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            });
        });
        
        requestAnimationFrame(animateParticles);
    }
    
    animateParticles();
}

// Loading screen
function showLoadingScreen() {
    const loadingDiv = document.createElement('div');
    loadingDiv.innerHTML = `
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                    background: var(--dark-bg); display: flex; justify-content: center; 
                    align-items: center; z-index: 9999;">
            <div class="loading-neural"></div>
        </div>
    `;
    document.body.appendChild(loadingDiv);
    return loadingDiv;
}

function hideLoadingScreen(loadingDiv) {
    if (loadingDiv) {
        loadingDiv.style.opacity = '0';
        setTimeout(() => {
            loadingDiv.remove();
        }, 300);
    }
}

// Success notification
function showSuccessNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'alert-neural alert-success';
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '10000';
    notification.style.minWidth = '300px';
    notification.innerHTML = `
        <strong>Success!</strong> ${message}
        <button type="button" style="float: right; background: none; border: none; color: white; font-size: 1.2rem; cursor: pointer;">&times;</button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
    
    // Manual close
    notification.querySelector('button').addEventListener('click', () => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    });
}

// Error notification
function showErrorNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'alert-neural alert-danger';
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '10000';
    notification.style.minWidth = '300px';
    notification.innerHTML = `
        <strong>Error!</strong> ${message}
        <button type="button" style="float: right; background: none; border: none; color: white; font-size: 1.2rem; cursor: pointer;">&times;</button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 7 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 7000);
    
    // Manual close
    notification.querySelector('button').addEventListener('click', () => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    });
}

// Form validation with neural styling
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('.form-control-neural[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = 'var(--neon-pink)';
            input.style.boxShadow = '0 0 20px rgba(255, 0, 110, 0.3)';
            isValid = false;
            
            // Remove error styling on input
            input.addEventListener('input', function() {
                this.style.borderColor = 'var(--glass-border)';
                this.style.boxShadow = 'none';
            });
        }
    });
    
    return isValid;
}

// Export functions for global use
window.NeuralTheme = {
    showLoadingScreen,
    hideLoadingScreen,
    showSuccessNotification,
    showErrorNotification,
    validateForm,
    createRippleEffect
};