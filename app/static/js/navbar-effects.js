/* ==== static/js/navbar-effects.js ============================== */
document.querySelectorAll(".navbar .nav-link, .navbar .navbar-brand").forEach(link => {
    link.addEventListener("mousemove", e => {
        const rect = link.getBoundingClientRect();
        const dx = (e.clientX - (rect.left + rect.width / 2)) / rect.width;
        const dy = (e.clientY - (rect.top  + rect.height / 2)) / rect.height;
        link.style.transform =
            `translate(${dx * 4}px, ${dy * 4}px) scale(1.08)`;
    });

    link.addEventListener("mouseleave", () => {
        link.style.transform = "";
    });
});