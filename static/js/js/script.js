// Basic utility functions

// Alert message show karna
function showMessage(message) {
    alert(message);
}

// Page smooth scroll (optional UI improvement)
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: "smooth" });
}

// Form validation helper
function isEmpty(value) {
    return value === null || value.trim() === "";
}