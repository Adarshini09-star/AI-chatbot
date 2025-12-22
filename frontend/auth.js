// ============================================================================
// AUTH.JS — FINAL WORKING VERSION
// Frontend + Backend served from SAME Flask origin
// ============================================================================

// NOTE:
// We DO NOT hardcode localhost:5000 anymore.
// We use SAME-ORIGIN relative paths.
// This removes ALL CORS / network issues.

console.log("🔐 Auth JS loaded");

// ============================================================================
// LOGIN
// ============================================================================

async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    const rememberMe = document.getElementById('rememberMe')?.checked;

    if (!email || !password) {
        showError('loginError', 'Please fill in all fields');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        hideLoading();

        if (!response.ok) {
            showError('loginError', data.error || 'Login failed');
            return;
        }

        const storage = rememberMe ? localStorage : sessionStorage;
        storage.setItem('user', JSON.stringify(data.user));
        storage.setItem('authToken', data.token || '');

        console.log('✅ Login successful');

        // Redirect to app page (Flask route)
        window.location.href = '/app';

    } catch (error) {
        hideLoading();
        console.error('LOGIN FETCH ERROR:', error);
        showError('loginError', 'Server not reachable');
    }
}

// ============================================================================
// REGISTER
// ============================================================================

async function handleRegister(event) {
    event.preventDefault();

    const name = document.getElementById('registerName').value.trim();
    const email = document.getElementById('registerEmail').value.trim();
    const password = document.getElementById('registerPassword').value;

    if (!name || !email || !password) {
        showError('registerError', 'Please fill in all fields');
        return;
    }

    if (password.length < 6) {
        showError('registerError', 'Password must be at least 6 characters');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();
        hideLoading();

        if (!response.ok) {
            showError('registerError', data.error || 'Registration failed');
            return;
        }

        console.log('✅ Registration successful');

        showSuccess('Account created! Please login.');
        setTimeout(() => switchForm('login'), 1000);

    } catch (error) {
        hideLoading();
        console.error('REGISTER FETCH ERROR:', error);
        showError('registerError', 'Server not reachable');
    }
}

// ============================================================================
// GUEST LOGIN (NO BACKEND REQUIRED)
// ============================================================================

function guestAccess() {
    const guestUser = {
        id: 'guest_' + Date.now(),
        name: 'Guest User',
        email: 'guest@careconnect.app',
        isGuest: true
    };

    sessionStorage.setItem('user', JSON.stringify(guestUser));
    sessionStorage.setItem('isGuest', 'true');

    console.log('👤 Guest access granted');

    window.location.href = '/app';
}

// ============================================================================
// UI HELPERS
// ============================================================================

function switchForm(type) {
    document.getElementById('loginForm').classList.toggle('active', type === 'login');
    document.getElementById('registerForm').classList.toggle('active', type === 'register');
    clearErrors();
}

function showError(id, message) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = '❌ ' + message;
    el.classList.add('active');
}

function showSuccess(message) {
    const toast = document.createElement('div');
    toast.className = 'success-message active';
    toast.textContent = '✅ ' + message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function clearErrors() {
    document.querySelectorAll('.error-message').forEach(el =>
        el.classList.remove('active')
    );
}

function showLoading() {
    document.getElementById('loadingOverlay')?.classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay')?.classList.remove('active');
}

// ============================================================================
// AUTO-REDIRECT IF ALREADY LOGGED IN
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    const user =
        sessionStorage.getItem('user') ||
        localStorage.getItem('user');

    if (user) {
        console.log('🔁 Already logged in → redirecting');
        window.location.href = '/app';
    }
});
