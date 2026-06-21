// Show welcome message
document.addEventListener("DOMContentLoaded", function () {
    console.log("User Panel Loaded");
});

// Simple form validation example
function validateProfileForm() {
    let name = document.querySelector("input[name='name']");
    let email = document.querySelector("input[name='email']");

    if (!name || name.value === "") {
        alert("Name is required");
        return false;
    }

    if (!email || email.value === "") {
        alert("Email is required");
        return false;
    }

    return true;
}

// Button click example
function updateProfile() {
    alert("Profile updated successfully!");
}