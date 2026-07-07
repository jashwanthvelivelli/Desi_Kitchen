// script.js - Minimal browser behavior for Desi Kitchen.
document.querySelectorAll("[data-confirm]").forEach(function (link) {
    link.addEventListener("click", function (event) {
        if (!confirm(link.dataset.confirm)) {
            event.preventDefault();
        }
    });
});
