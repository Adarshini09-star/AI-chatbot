// auth-check.js
document.addEventListener('DOMContentLoaded', () => {
    const user =
        sessionStorage.getItem('user') ||
        localStorage.getItem('user');

    const isGuest = sessionStorage.getItem('isGuest');

    if (!user && !isGuest) {
        window.location.replace('login.html');
        return;
    }

    console.log('✅ Authenticated');
});
