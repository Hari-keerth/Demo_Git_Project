

// Password Validation
function checkPassword() {
    if (passInput.value.trim() === "") {
        passField.classList.add("invalid");
    } else {
        passField.classList.remove("invalid");
    }
}

// Show / Hide Password
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

// Form Submit
form.addEventListener("submit", (e) => {

    e.preventDefault();

    checkEmail();
    checkPassword();

    if (
        !emailField.classList.contains("invalid") &&
        !passField.classList.contains("invalid")
    ) {
        alert("Login Successful!");
        // location.href = "home.html";
    }
});

// Live Validation
emailInput.addEventListener("keyup", checkEmail);
passInput.addEventListener("keyup", checkPassword);