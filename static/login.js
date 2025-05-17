document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("loginForm");
    form.addEventListener("submit", function (e) {
        e.preventDefault();  // Prevent page reload

        const username = document.getElementById("username").value.trim();
        if (!username) {
            alert("Please enter a username.");
            return;
        }

        // Send POST request to /login
        fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `username=${encodeURIComponent(username)}`
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                alert("Login failed or server did not redirect.");
            }
        })
        .catch(err => console.error("Login error:", err));
    });
});
