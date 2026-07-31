const form = document.querySelector("form");

const emailField = form.querySelector(".email-field");
const emailInput = form.querySelector(".email");

const passField = form.querySelector(".create-password");
const passInput = form.querySelector(".password");

const cPassField = form.querySelector(".confirm-password");
const cPassInput = form.querySelector(".cPassword");

// ==================== Email Validation ====================
function checkEmail() {
    const emailPattern = /^[^ ]+@[^ ]+\.[a-z]{2,3}$/;

    if (!emailPattern.test(emailInput.value)) {
        emailField.classList.add("invalid");
    } else {
        emailField.classList.remove("invalid");
    }
}

// ==================== Password Validation ====================
function createPass() {

    const passPattern =
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

    if (!passPattern.test(passInput.value)) {
        passField.classList.add("invalid");
    } else {
        passField.classList.remove("invalid");
    }
}

// ==================== Confirm Password ====================
function confirmPass() {

    if (
        passInput.value !== cPassInput.value ||
        cPassInput.value === ""
    ) {
        cPassField.classList.add("invalid");
    } else {
        cPassField.classList.remove("invalid");
    }
}

// ==================== Show / Hide Password ====================
const eyeIcons = document.querySelectorAll(".show-hide");

eyeIcons.forEach((eyeIcon) => {

    eyeIcon.addEventListener("click", () => {

        const input = eyeIcon.parentElement.querySelector("input");

        if (input.type === "password") {
            input.type = "text";
            eyeIcon.classList.replace("bx-hide", "bx-show");
        } else {
            input.type = "password";
            eyeIcon.classList.replace("bx-show", "bx-hide");
        }

    });

});

// ==================== Live Validation ====================
emailInput.addEventListener("keyup", checkEmail);

passInput.addEventListener("keyup", () => {
    createPass();
    confirmPass();
});

cPassInput.addEventListener("keyup", confirmPass);

// ==================== Form Submit ====================
form.addEventListener("submit", (e) => {

    e.preventDefault();

    checkEmail();
    createPass();
    confirmPass();

    if (
        !emailField.classList.contains("invalid") &&
        !passField.classList.contains("invalid") &&
        !cPassField.classList.contains("invalid")
    ) {

        alert("Registration Successful!");

        // Redirect after successful registration
        // location.href = "login.html";

        form.reset();

    }

});