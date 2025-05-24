document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("loginForm");
    form.addEventListener("submit", function (e) {
        e.preventDefault();  // Prevent page reload

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();  

        if (!username) {
            alert("Please enter a username.");
            return;
        }
        if (!password) {
            alert("Please enter a password.");
            return;
        }

        // Send POST request to /login with JSON
        fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === "Login successful") {
                // Redirect to /home on success
                window.location.href = '/home';
            } else if (data.error) {
                alert("Login failed: " + data.error);
            } else {
                alert("Login failed: Unknown error");
            }
        })
        .catch(err => {
            console.error("Login error:", err);
            alert("An error occurred. Please try again.");
        });
    });
});

