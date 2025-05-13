// static/js/homepage.js

// Execute after the page has finished loading
document.addEventListener('DOMContentLoaded', function () {

    // --------------------------------------------------
    // 1. Bootstrap Dropdown on Hover Logic (Your existing code)
    // --------------------------------------------------
    var dropdowns = document.querySelectorAll('.dropdown');

    dropdowns.forEach(function (dropdown) {
        var toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]'); // Get toggle once

        // Check if a toggle button actually exists within this dropdown
        if (toggle) {
            var dropdownInstance = null; // To store the instance

            dropdown.addEventListener('mouseover', function () {
                // Get or create instance only when needed
                if (!dropdownInstance) {
                    dropdownInstance = bootstrap.Dropdown.getOrCreateInstance(toggle);
                }
                dropdownInstance.show();
            });

            dropdown.addEventListener('mouseleave', function () {
                // Get or create instance only when needed
                if (!dropdownInstance) {
                    dropdownInstance = bootstrap.Dropdown.getOrCreateInstance(toggle);
                }
                // A small delay can prevent the dropdown from closing if the mouse briefly leaves and re-enters
                setTimeout(function() {
                    if (!dropdown.matches(':hover')) { // Check if mouse is truly outside
                        dropdownInstance.hide();
                    }
                }, 100); // 100ms delay, adjust as needed
            });
        }
    });

    // --------------------------------------------------
    // 2. Scroll Animation Logic (Intersection Observer)
    // --------------------------------------------------
    const revealElements = document.querySelectorAll('.reveal-on-scroll');

    if (revealElements.length > 0) {
        const revealObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    // Optional: Unobserve after revealed to save resources,
                    // especially if you don't want the animation to re-trigger.
                    // observer.unobserve(entry.target);
                }
                // Optional: To re-trigger animation when scrolling up and element is out of view again
                // else {
                //     // Check if the element is truly out of the viewport
                //     if (entry.boundingClientRect.top > window.innerHeight || entry.boundingClientRect.bottom < 0) {
                //        entry.target.classList.remove('revealed');
                //     }
                // }
            });
        }, {
            threshold: 0.1, // Trigger when 10% of the element is visible. Adjust (0.0 to 1.0) as needed.
            // rootMargin: "0px 0px -50px 0px" // Optional: Adjust when the intersection is calculated (e.g., trigger 50px before it's fully in view from the bottom)
        });

        revealElements.forEach(el => {
            revealObserver.observe(el);
        });
    }

}); // End of DOMContentLoaded

