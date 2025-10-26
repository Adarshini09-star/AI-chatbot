// ============================================================================
// CONFIGURATION
// ============================================================================

// Toggle demo mode (for offline testing without backend)
const DEMO_MODE = false;

// Automatically detect backend host and port
const API_HOST = window.location.hostname;
const API_PORT = 5000;
const API_URL = `http://${API_HOST}:${API_PORT}/api`;

console.log("🔗 Connecting to backend at:", API_URL);

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

let currentUser = null;
let sessionId = null;
let chatHistory = [];
let isTyping = false;
let recognition = null;

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkExistingSession();
});

function initializeApp() {
    // Initialize textarea auto-resize
    const textarea = document.getElementById('messageInput');
    if (textarea) {
        textarea.addEventListener('input', autoResizeTextarea);
        textarea.addEventListener('input', updateCharCounter);
        textarea.addEventListener('keydown', handleEnterKey);
    }
    
    console.log('🏥 HealthCare AI Assistant initialized');
}

function setupEventListeners() {
    // Only set up if elements exist
    const loginForm = document.getElementById('loginFormElement');
    const registerForm = document.getElementById('registerFormElement');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
}

function checkExistingSession() {
    const token = sessionStorage.getItem('authToken');
    const user = sessionStorage.getItem('user');
    
    if (token && user) {
        currentUser = JSON.parse(user);
        sessionId = generateSessionId();
        if (typeof showMainApp === 'function') showMainApp();
        if (typeof loadHealthNews === 'function') loadHealthNews();
        if (typeof showToast === 'function') {
            showToast('Welcome back, ' + currentUser.name + '! 👋', 'success');
        }
    } else {
        // Generate session ID even if not logged in
        sessionId = generateSessionId();
    }
}

// ============================================================================
// AUTHENTICATION
// ============================================================================

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    
    if (!email || !password) {
        showError('loginError', 'Please enter email and password');
        return;
    }
    
    showLoadingOverlay();
    
    try {
        if (DEMO_MODE) {
            // Demo mode - simulate login
            setTimeout(() => {
                simulateLogin(email);
            }, 1000);
        } else {
            // Real API call
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                handleLoginSuccess(data);
            } else {
                hideLoadingOverlay();
                showError('loginError', data.message || 'Login failed');
            }
        }
    } catch (error) {
        hideLoadingOverlay();
        showError('loginError', 'Network error. Please try again.');
        console.error('Login error:', error);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
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
    
    showLoadingOverlay();
    
    try {
        if (DEMO_MODE) {
            setTimeout(() => {
                simulateLogin(email, name);
                showToast('Account created successfully! 🎉', 'success');
            }, 1000);
        } else {
            const response = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                hideLoadingOverlay();
                showToast('Account created! Please login.', 'success');
                showLogin();
            } else {
                hideLoadingOverlay();
                showError('registerError', data.message || 'Registration failed');
            }
        }
    } catch (error) {
        hideLoadingOverlay();
        showError('registerError', 'Network error. Please try again.');
        console.error('Register error:', error);
    }
}

function simulateLogin(email, name = null) {
    const user = {
        id: Date.now().toString(),
        name: name || email.split('@')[0],
        email: email
    };
    
    const token = 'demo_token_' + Date.now();
    
    sessionStorage.setItem('authToken', token);
    sessionStorage.setItem('user', JSON.stringify(user));
    
    currentUser = user;
    sessionId = generateSessionId();
    
    hideLoadingOverlay();
    showMainApp();
    if (typeof loadHealthNews === 'function') loadHealthNews();
    showToast('Welcome, ' + user.name + '! 🏥', 'success');
}

function handleLoginSuccess(data) {
    sessionStorage.setItem('authToken', data.token);
    sessionStorage.setItem('user', JSON.stringify(data.user));
    
    currentUser = data.user;
    sessionId = data.sessionId || generateSessionId();
    
    hideLoadingOverlay();
    showMainApp();
    if (typeof loadHealthNews === 'function') loadHealthNews();
    showToast('Welcome back, ' + data.user.name + '! 👋', 'success');
}

function logout() {
    sessionStorage.clear();
    currentUser = null;
    sessionId = generateSessionId();
    chatHistory = [];
    
    const mainApp = document.getElementById('mainApp');
    const authModal = document.getElementById('authModal');
    const messagesArea = document.getElementById('messagesArea');
    
    if (mainApp) mainApp.style.display = 'none';
    if (authModal) authModal.classList.add('active');
    
    // Clear messages
    if (messagesArea && typeof getWelcomeMessage === 'function') {
        messagesArea.innerHTML = getWelcomeMessage();
    }
    
    showToast('Logged out successfully. See you soon! 👋', 'success');
}

function showLogin() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (registerForm) registerForm.style.display = 'none';
    if (loginForm) loginForm.style.display = 'block';
}

function showRegister() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (loginForm) loginForm.style.display = 'none';
    if (registerForm) registerForm.style.display = 'block';
}

function showMainApp() {
    const authModal = document.getElementById('authModal');
    const mainApp = document.getElementById('mainApp');
    const userName = document.getElementById('userName');
    
    if (authModal) authModal.classList.remove('active');
    if (mainApp) mainApp.style.display = 'flex';
    if (userName && currentUser) userName.textContent = currentUser.name;
}

// ============================================================================
// CHAT FUNCTIONALITY
// ============================================================================

async function sendMessage(messageText) {
    // Get message from input if not provided
    const message = messageText || document.getElementById("messageInput")?.value?.trim();
    
    if (!message) return;
    
    const chatWindow = document.getElementById("messagesArea") || document.getElementById("chat-window");
    const messageInput = document.getElementById("messageInput");
    
    if (!chatWindow) {
        console.error("Chat window not found");
        return;
    }
    
    // Clear input
    if (messageInput && !messageText) {
        messageInput.value = '';
    }

    // Show user message
    addMessageToChat(message, 'user');

    // Show typing indicator
    showTypingIndicator();

    try {
        // Use dynamic API_URL instead of hardcoded
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId || "user123",
            }),
        });

        const data = await response.json();

        // Hide typing indicator
        hideTypingIndicator();

        // Show bot message
        addMessageToChat(data.response || data.reply || "⚠️ No reply received.", 'bot');

    } catch (error) {
        hideTypingIndicator();
        
        addMessageToChat(`❌ Error: Could not connect to backend at ${API_URL}`, 'bot');
        
        console.error("Chat error:", error);
    }
}

function addMessageToChat(text, sender) {
    const messagesArea = document.getElementById('messagesArea') || document.getElementById('chat-window');
    
    if (!messagesArea) return;
    
    // Remove welcome message if it exists
    const welcomeMsg = messagesArea.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const timestamp = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    // Format the text
    let formattedText = escapeHtml(text);
    formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formattedText = formattedText.replace(/\n/g, '<br>');
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${sender === 'user' ? '👤' : '🤖'}</div>
        <div>
            <div class="message-content">${formattedText}</div>
            ${timestamp ? `<div class="message-timestamp">${timestamp}</div>` : ''}
        </div>
    `;
    
    messagesArea.appendChild(messageDiv);
    scrollToBottom();
}

function showTypingIndicator() {
    const messagesArea = document.getElementById('messagesArea') || document.getElementById('chat-window');
    
    if (!messagesArea) return;
    
    // Remove existing typing indicator
    hideTypingIndicator();
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="typing-indicator active">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    
    messagesArea.appendChild(typingDiv);
    scrollToBottom();
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function sendQuickQuestion(question) {
    sendMessage(question);
}

function scrollToBottom() {
    const messagesArea = document.getElementById('messagesArea') || document.getElementById('chat-window');
    if (messagesArea) {
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================================
// DEMO RESPONSE GENERATOR
// ============================================================================

function generateDemoResponse(message) {
    const lowerMessage = message.toLowerCase();
    
    const responses = {
        'cold': "🤧 Common cold symptoms include:\n\n• Runny or stuffy nose\n• Sore throat\n• Cough\n• Mild fever\n• Fatigue\n• Sneezing\n\nTreatment tips:\n✓ Rest and stay hydrated\n✓ Drink warm fluids (tea, soup)\n✓ Use over-the-counter medications if needed\n✓ Get plenty of sleep\n\n⚠️ Consult a doctor if symptoms persist beyond 10 days or worsen.",
        
        'stress': "😌 Here are effective ways to reduce stress:\n\n1. Deep Breathing: Practice 4-7-8 breathing technique\n2. Exercise: 30 minutes daily of moderate activity\n3. Sleep: Maintain 7-8 hours per night\n4. Meditation: Try mindfulness for 10 minutes daily\n5. Social Connection: Talk to friends and family\n6. Time Management: Prioritize tasks and take breaks\n7. Hobbies: Engage in activities you enjoy\n\n💙 Remember: It's okay to seek professional help if stress becomes overwhelming.",
        
        'diet': "🥗 Healthy Diet Tips:\n\n**What to Include:**\n✓ Colorful fruits and vegetables (5+ servings daily)\n✓ Whole grains (brown rice, quinoa, oats)\n✓ Lean proteins (fish, chicken, legumes)\n✓ Healthy fats (nuts, avocado, olive oil)\n✓ 8-10 glasses of water\n\n**What to Limit:**\n✗ Processed foods\n✗ Added sugars\n✗ Excessive salt\n✗ Trans fats\n✗ Alcohol\n\n💡 Eat regular, balanced meals and practice portion control!",
        
        'exercise': "💪 Exercise Recommendations:\n\n**Cardio (150 min/week):**\n• Brisk walking\n• Jogging\n• Cycling\n• Swimming\n• Dancing\n\n**Strength Training (2x/week):**\n• Weight lifting\n• Resistance bands\n• Bodyweight exercises\n• Yoga\n\n**Tips for Success:**\n✓ Start slowly and build up\n✓ Find activities you enjoy\n✓ Set realistic goals\n✓ Stay consistent\n✓ Warm up and cool down\n✓ Listen to your body\n\n🏃‍♀️ Always consult a doctor before starting a new exercise program!",
        
        'sleep': "😴 Better Sleep Tips:\n\n**Bedtime Routine:**\n• Go to bed at the same time daily\n• Create a relaxing pre-sleep ritual\n• Avoid screens 1 hour before bed\n• Keep bedroom cool (65-68°F)\n• Use blackout curtains\n\n**Diet & Lifestyle:**\n• Limit caffeine after 2 PM\n• Avoid heavy meals before bed\n• Exercise regularly (but not close to bedtime)\n• Manage stress\n• Get natural sunlight during the day\n\n**If You Can't Sleep:**\n• Get up and do a quiet activity\n• Try progressive muscle relaxation\n• Practice deep breathing\n\n💤 Aim for 7-9 hours of quality sleep!",
        
        'headache': "🧠 Headache Relief:\n\n**Immediate Relief:**\n• Rest in a quiet, dark room\n• Apply cold or warm compress\n• Stay hydrated\n• Take deep breaths\n• Gentle neck stretches\n\n**Prevention:**\n• Manage stress\n• Regular sleep schedule\n• Stay hydrated\n• Limit screen time\n• Maintain good posture\n• Regular meals\n\n⚠️ **Seek medical attention if:**\n• Sudden severe headache\n• Headache with fever, stiff neck, or confusion\n• Headache after head injury\n• Frequent or worsening headaches\n\nOver-the-counter pain relievers may help, but consult a doctor for chronic headaches.",
        
        'diabetes': "🩺 Diabetes Management:\n\n**Blood Sugar Control:**\n• Monitor levels regularly\n• Follow prescribed medication\n• Eat balanced meals\n• Control portion sizes\n• Limit refined sugars\n\n**Healthy Lifestyle:**\n• Exercise 150 minutes/week\n• Maintain healthy weight\n• Manage stress\n• Get adequate sleep\n• Stay hydrated\n\n**Regular Check-ups:**\n• A1C tests every 3-6 months\n• Eye exams annually\n• Foot checks\n• Blood pressure monitoring\n\n💙 Work closely with your healthcare team for personalized care!",
        
        'anxiety': "💙 Managing Anxiety:\n\n**Immediate Techniques:**\n1. Deep breathing (4-4-4 method)\n2. Grounding exercises (5-4-3-2-1)\n3. Progressive muscle relaxation\n4. Walking or gentle movement\n\n**Long-term Strategies:**\n• Regular exercise\n• Adequate sleep\n• Balanced diet\n• Limit caffeine & alcohol\n• Mindfulness meditation\n• Social connection\n• Time in nature\n\n**When to Seek Help:**\n• Anxiety interferes with daily life\n• Physical symptoms persist\n• Panic attacks\n• Avoiding situations\n\n🌟 Remember: Seeking professional help is a sign of strength, not weakness!",
        
        'heart': "❤️ Heart Health Tips:\n\n**Exercise:**\n• 150 min moderate activity/week\n• Include strength training\n• Stay active throughout the day\n\n**Diet:**\n• Fruits & vegetables\n• Whole grains\n• Lean proteins\n• Healthy fats (omega-3)\n• Limit sodium & saturated fats\n\n**Lifestyle:**\n• Don't smoke\n• Limit alcohol\n• Manage stress\n• Maintain healthy weight\n• Get 7-9 hours sleep\n• Control blood pressure\n\n**Regular Monitoring:**\n• Check blood pressure\n• Monitor cholesterol\n• Blood sugar levels\n• Annual check-ups\n\n💪 Small changes can make a big difference for your heart!"
    };
    
    // Check for keywords
    for (const [keyword, response] of Object.entries(responses)) {
        if (lowerMessage.includes(keyword)) {
            return response;
        }
    }
    
    // Check for greetings
    if (lowerMessage.match(/\b(hi|hello|hey|greetings)\b/)) {
        const name = currentUser ? currentUser.name : 'there';
        return `Hello ${name}! 👋 How can I help you today? I can assist with:\n\n• Health symptoms and conditions\n• Diet and nutrition advice\n• Exercise recommendations\n• Stress and mental health\n• Finding nearby hospitals\n• Emergency helplines\n\nWhat would you like to know?`;
    }
    
    // Check for thanks
    if (lowerMessage.match(/\b(thank|thanks|appreciate)\b/)) {
        return "You're very welcome! 😊 I'm here 24/7 to help with your health questions. Is there anything else you'd like to know?";
    }
    
    // Default response
    return "I'm here to help with your health questions! You can ask me about:\n\n• Symptoms and conditions\n• Diet and nutrition\n• Exercise and fitness\n• Stress management\n• Sleep problems\n• Finding healthcare providers\n\nOr use the quick access buttons on the sidebar for hospitals, doctors, and emergency helplines. What would you like to know? 💙";
}

// ============================================================================
// FILE UPLOAD
// ============================================================================

async function handleFileUpload(input, type) {
    const file = input.files[0];
    if (!file) return;
    
    const maxSize = 16 * 1024 * 1024; // 16MB
    if (file.size > maxSize) {
        showToast('File size must be less than 16MB', 'error');
        input.value = '';
        return;
    }
    
    addMessageToChat(`📎 Uploading ${file.name}...`, 'user');
    showTypingIndicator();
    
    try {
        if (DEMO_MODE) {
            setTimeout(() => {
                hideTypingIndicator();
                const response = type === 'image' 
                    ? `📷 Image "${file.name}" received!\n\nI can see this is a medical image. For accurate medical diagnosis from images, please consult a healthcare professional who can properly examine the image and your symptoms.\n\nI can provide general health information. What would you like to know?`
                    : `📄 PDF "${file.name}" received!\n\nI've noted your medical document. For detailed interpretation of medical reports and test results, please consult your doctor who can provide personalized medical advice.\n\nI can answer general questions about medical terminology. How can I help?`;
                
                addMessageToChat(response, 'bot');
                showToast('File uploaded successfully! 📎', 'success');
            }, 2000);
        } else {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('sessionId', sessionId);
            formData.append('type', type);
            
            const response = await fetch(`${API_URL}/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer ' + sessionStorage.getItem('authToken')
                },
                body: formData
            });
            
            const data = await response.json();
            
            hideTypingIndicator();
            
            if (response.ok) {
                addMessageToChat(data.analysis || 'File uploaded successfully!', 'bot');
                showToast('File uploaded successfully! 📎', 'success');
            } else {
                addMessageToChat('Failed to upload file. Please try again.', 'bot');
                showToast('Upload failed', 'error');
            }
        }
    } catch (error) {
        hideTypingIndicator();
        addMessageToChat('Error uploading file. Please try again.', 'bot');
        console.error('Upload error:', error);
    }
    
    input.value = '';
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.classList.add('active');
        setTimeout(() => {
            element.classList.remove('active');
        }, 5000);
    }
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (toast) {
        toast.textContent = message;
        toast.className = 'toast show ' + type;
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    } else {
        console.log('Toast:', message);
    }
}

function showLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.style.display = 'flex';
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.style.display = 'none';
}

function autoResizeTextarea(e) {
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
}

function updateCharCounter(e) {
    const textarea = e.target;
    const counter = document.getElementById('charCount');
    if (counter) {
        const count = textarea.value.length;
        counter.textContent = `${count}/500`;
        if (count > 500) {
            counter.style.color = 'red';
        } else {
            counter.style.color = '';
        }
    }
}

function handleEnterKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

function initVoiceRecognition() {
    // Voice recognition initialization
    // To be implemented if needed
    console.log('Voice recognition: Not implemented yet');
}

function loadHealthNews() {
    // Load health news
    // To be implemented if needed
    console.log('Health news: Not implemented yet');
}

function getWelcomeMessage() {
    return `
        <div class="message bot">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                Hello! 👋 I'm your AI Public Health Assistant.<br><br>
                I can help you with:<br>
                ✅ Disease information<br>
                ✅ Symptoms and prevention tips<br>
                ✅ Health guidance<br><br>
                What would you like to know about today?
            </div>
        </div>
    `;
}

// Sidebar functions
function findNearbyHospitals() {
    sendQuickQuestion('Show me nearby hospitals');
}

function findNearbyDoctors() {
    sendQuickQuestion('Show me nearby doctors');
}

function showHelplines() {
    addMessageToChat('Emergency helplines', 'user');
    setTimeout(() => {
        addMessageToChat('🚨 Emergency Helplines:\n\n• India Emergency: 112\n• Ambulance: 108\n• Police: 100\n• Fire: 101\n• Women Helpline: 1091\n• Child Helpline: 1098\n• Mental Health: 1800-599-0019', 'bot');
    }, 500);
}

function showAyurvedicTips() {
    sendQuickQuestion('Give me ayurvedic health tips');
}

function showDietPlans() {
    sendQuickQuestion('Suggest a healthy diet plan');
}

console.log('✅ Script loaded successfully');