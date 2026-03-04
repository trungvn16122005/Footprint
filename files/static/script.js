//Terry
document.addEventListener('DOMContentLoaded', () => {
    const loginModal = document.getElementById("loginModal");

// If login modal has flashes, open it
    if (loginModal?.querySelector(".modalFlashes")?.children.length > 0) {
        loginModal.style.display = "flex";
    }

    // ===== Theme toggle =====
    const toggle = document.getElementById("themeToggle");
    toggle?.addEventListener("click", () => document.body.classList.toggle("dark"));

    // ===== Open login modal =====
    const loginBtn = document.getElementById("logInBtn");
    loginBtn?.addEventListener("click", e => {
        e.preventDefault();
        const loginModal = document.getElementById("loginModal");
        if (loginModal) loginModal.style.display = "flex";
    });

    // ===== Open signup modal =====
    const signUpBtn = document.getElementById("signUpBtn");
    signUpBtn?.addEventListener("click", e => {
        e.preventDefault();
        const signupModal = document.getElementById("signupModal");
        if (signupModal) signupModal.style.display = "flex";
    });

//Khang
    // ===== "Create one" link inside login opens signup =====
    const openSignupLink = document.getElementById("openSignupLink");
    openSignupLink?.addEventListener("click", e => {
        e.preventDefault();
        const loginModal = document.getElementById("loginModal");
        const signupModal = document.getElementById("signupModal");
        if (loginModal) loginModal.style.display = "none";
        if (signupModal) signupModal.style.display = "flex";
    });

    // ===== Close modals =====
    document.querySelectorAll(".modal .close").forEach(btn => {
        btn.addEventListener("click", e => {
            const modal = e.target.closest(".modal");
            if (modal) modal.style.display = "none";
        });
    });

    // ===== Close modals when clicking outside =====
    document.querySelectorAll(".modal").forEach(modal => {
        modal.addEventListener("click", e => {
            if (e.target === modal) modal.style.display = "none";
        });
    });

    // ===== Logout button =====
    const logOutBtn = document.getElementById("logOutBtn");
    logOutBtn?.addEventListener("click", () => window.location.href = "/logout");

    // ===== Signup Form Validation =====
    const signupModal = document.getElementById("signupModal");
    const signupForm = signupModal?.querySelector("form");

    if (signupForm) {
        signupForm.addEventListener("submit", (e) => {
            // Clear previous errors
            clearFormErrors(signupForm);

            const username = signupForm.querySelector('input[name="username"]').value.trim();
            const email = signupForm.querySelector('input[name="email"]').value.trim();
            const password = signupForm.querySelector('input[name="password"]').value;
            const confirmPassword = signupForm.querySelector('input[name="confirm_password"]').value;

            const errors = [];

            // Username validation
            if (!username) {
                errors.push("Username is required.");
            } else if (username.length < 3 || username.length > 30) {
                errors.push("Username must be 3-30 characters.");
            } else if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
                errors.push("Username can only contain letters, numbers, underscores, and hyphens.");
            }

            // Email validation
            if (!email) {
                errors.push("Email is required.");
            } else if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
                errors.push("Invalid email format.");
            }

            // Password validation
            if (!password) {
                errors.push("Password is required.");
            } else {
                if (password.length < 8) {
                    errors.push("Password must be at least 8 characters.");
                }
                if (!/[A-Z]/.test(password)) {
                    errors.push("Password must contain at least one uppercase letter.");
                }
                if (!/[a-z]/.test(password)) {
                    errors.push("Password must contain at least one lowercase letter.");
                }
                if (!/\d/.test(password)) {
                    errors.push("Password must contain at least one number.");
                }
            }

            // Confirm password
            if (password !== confirmPassword) {
                errors.push("Passwords do not match.");
            }

            // If errors, prevent submit and show them
            if (errors.length > 0) {
                e.preventDefault();
                showFormErrors(signupForm, errors);
            }
        });
    }

    // ===== Helper: Show form errors inline =====
    function showFormErrors(form, errors) {
        let errorDiv = form.querySelector(".form-errors");
        if (!errorDiv) {
            errorDiv = document.createElement("div");
            errorDiv.className = "form-errors";
            form.insertBefore(errorDiv, form.firstChild);
        }
        errorDiv.innerHTML = errors.map(err => `<div class="form-error">${err}</div>`).join("");
    }

    // ===== Helper: Clear form errors =====
    function clearFormErrors(form) {
        const errorDiv = form.querySelector(".form-errors");
        if (errorDiv) {
            errorDiv.innerHTML = "";
        }
    }

  });
  