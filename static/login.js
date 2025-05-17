document.getElementById('loginForm').addEventListener('submit', function(e){
    const ussername= document.getElementById('username').ariaValueMax.trim();
    if (!username) {
        e.preventDefault();
        alert('Please enter a username');
        alert("login.js loaded!");

    }
});