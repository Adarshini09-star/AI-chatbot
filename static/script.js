// ============================================================================
// CARECONNECT - MAIN APPLICATION (NO AUTH LOGIC HERE)
// ============================================================================

// Configuration
const API_HOST = window.location.hostname || '127.0.0.1';
const API_PORT = 5000;
const API_URL = `http://${API_HOST}:${API_PORT}/api`;

let sessionId = 'session_' + Date.now();
let currentLang = 'en';

console.log("🔗 Connecting to backend at:", API_URL);

// ============================================================================
// LANGUAGE MANAGEMENT
// ============================================================================

function translate(key) {
    return translations[currentLang][key] || translations['en'][key] || key;
}

function updateUILanguage() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[currentLang][key]) {
            el.innerHTML = translations[currentLang][key];
        }
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (translations[currentLang][key]) {
            el.placeholder = translations[currentLang][key];
        }
    });

    const messagesArea = document.getElementById('messagesArea');
    messagesArea.innerHTML = '';
    addWelcomeMessage();
}

function toggleLanguage() {
    currentLang = currentLang === 'en' ? 'hi' : 'en';
    localStorage.setItem('language', currentLang);

    document.getElementById('langText').textContent =
        currentLang === 'en' ? 'हिंदी' : 'English';

    updateUILanguage();
    showToast(translate('langChanged'));
}

// ============================================================================
// THEME MANAGEMENT
// ============================================================================

function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    document.getElementById('themeIcon').textContent =
        newTheme === 'dark' ? '☀️' : '🌙';

    showToast(newTheme === 'dark'
        ? translate('darkModeOn')
        : translate('lightModeOn'));
}

// ============================================================================
// CHAT FUNCTIONALITY
// ============================================================================

async function sendMessage(messageText) {
    const message =
        messageText ||
        document.getElementById("messageInput")?.value?.trim();

    if (!message) return;

    const input = document.getElementById("messageInput");
    if (input && !messageText) input.value = '';

    addMessageToChat(message, 'user');
    showTypingIndicator();

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message,
                session_id: sessionId
            })
        });

        const data = await response.json();
        hideTypingIndicator();
        addMessageToChat(
            data.response || data.reply || "⚠️ No reply received.",
            'bot',
            true
        );

    } catch (error) {
        hideTypingIndicator();
        addMessageToChat("❌ Backend not reachable.", 'bot');
        console.error(error);
    }
}

function addMessageToChat(text, sender, addFeedback = false) {
    const area = document.getElementById('messagesArea');
    if (!area) return;

    const div = document.createElement('div');
    div.className = `message ${sender}`;
    const id = 'msg_' + Date.now();

    let formatted = escapeHtml(text)
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');

    div.id = id;
    div.innerHTML = `
        <div class="message-avatar">${sender === 'user' ? '👤' : '🤖'}</div>
        <div>
            <div class="message-content">${formatted}</div>
        </div>
    `;

    area.appendChild(div);
    scrollToBottom();
}

// ============================================================================
// UI HELPERS
// ============================================================================

function showTypingIndicator() {
    const area = document.getElementById('messagesArea');
    hideTypingIndicator();

    const div = document.createElement('div');
    div.id = 'typingIndicator';
    div.className = 'message bot';
    div.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    area.appendChild(div);
}

function hideTypingIndicator() {
    document.getElementById('typingIndicator')?.remove();
}

function sendQuickQuestion(q) {
    sendMessage(q);
}

function showEmergencyInfo() {
    addMessageToChat(translate('emergencyInfo'), 'bot');
}

function scrollToBottom() {
    const area = document.getElementById('messagesArea');
    area.scrollTop = area.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    setTimeout(() => toast.classList.remove('show'), 3000);
}

function addWelcomeMessage() {
    const area = document.getElementById('messagesArea');
    const div = document.createElement('div');
    div.className = 'message bot';
    div.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            ${translate('welcomeMsg').replace(/\n/g, '<br>')}
        </div>
    `;
    area.appendChild(div);
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
    document.getElementById('themeIcon').textContent =
        theme === 'dark' ? '☀️' : '🌙';

    currentLang = localStorage.getItem('language') || 'en';
    document.getElementById('langText').textContent =
        currentLang === 'en' ? 'हिंदी' : 'English';

    updateUILanguage();
    console.log('✅ CareConnect loaded cleanly');
});
