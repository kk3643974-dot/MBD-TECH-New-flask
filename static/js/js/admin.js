// Delete confirmation for admin actions
function confirmDelete() {
    return confirm("Are you sure you want to delete this?");
}

// Example: user delete button handling
document.addEventListener("DOMContentLoaded", function () {
    const deleteButtons = document.querySelectorAll("button");

    deleteButtons.forEach(btn => {
        if (btn.innerText.toLowerCase() === "delete") {
            btn.addEventListener("click", function (e) {
                if (!confirmDelete()) {
                    e.preventDefault();
                }
            });
        }
    });
});

// Admin dashboard greeting
console.log("Admin Panel Loaded Successfully");