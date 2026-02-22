document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.home-slideshow');
    if (!container) return;

    const slides = Array.from(container.querySelectorAll('.home-slideshow-link'));
    if (slides.length === 0) return;

    for (let i = slides.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [slides[i], slides[j]] = [slides[j], slides[i]];
    }
    slides.forEach(slide => container.appendChild(slide));

    let currentIndex = 0;
    const displayDuration = 5300;

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.toggle('active', i === index);
        });
    }

    function nextSlide() {
        currentIndex = (currentIndex + 1) % slides.length;
        showSlide(currentIndex);
    }

    showSlide(0);
    setInterval(nextSlide, displayDuration);
});
