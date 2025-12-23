from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Initialize Flask app
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("⚠️ WARNING: GEMINI_API_KEY not found in .env file!")
    print("⚠️ Chatbot will fall back to static responses.")
    USE_AI = False
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Use the new model name for latest API
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        USE_AI = True
        print("✅ Gemini AI initialized successfully!")
    except Exception as e:
        print(f"⚠️ Gemini AI initialization failed: {e}")
        print("⚠️ Chatbot will fall back to static responses.")
        USE_AI = False

# In-memory session storage
sessions = {}

# ==================== DISEASE KNOWLEDGE BASE ====================
DISEASES = {
    "covid-19": {
        "name": "COVID-19",
        "description": "COVID-19 is a respiratory illness caused by the SARS-CoV-2 virus.",
        "symptoms": ["Fever or chills", "Cough", "Shortness of breath", "Fatigue", "Loss of taste or smell"],
        "prevention": ["Get vaccinated", "Wear masks", "Maintain distance", "Wash hands frequently"],
    },
    "diabetes": {
        "name": "Diabetes",
        "description": "Diabetes is a chronic disease affecting blood glucose levels.",
        "symptoms": ["Increased thirst", "Frequent urination", "Extreme hunger", "Unexplained weight loss", "Fatigue"],
        "prevention": ["Maintain healthy weight", "Exercise regularly", "Balanced diet", "Limit sugar"],
    },
    "tuberculosis": {
        "name": "Tuberculosis (TB)",
        "description": "TB is a bacterial infection primarily affecting the lungs.",
        "symptoms": ["Persistent cough", "Coughing up blood", "Chest pain", "Weight loss", "Night sweats"],
        "prevention": ["BCG vaccine", "Avoid close contact with TB patients", "Good ventilation"],
    },
    "malaria": {
        "name": "Malaria",
        "description": "Malaria is caused by parasites transmitted through mosquito bites.",
        "symptoms": ["High fever", "Chills", "Severe headache", "Nausea", "Muscle pain"],
        "prevention": ["Use mosquito nets", "Apply repellent", "Wear protective clothing", "Take antimalarial medication"],
    },
    "dengue": {
        "name": "Dengue Fever",
        "description": "Dengue is a mosquito-borne viral infection.",
        "symptoms": ["High fever", "Severe headache", "Pain behind eyes", "Joint pain", "Skin rash"],
        "prevention": ["Remove standing water", "Use mosquito repellent", "Wear long sleeves"],
    },
}

# ==================== EMERGENCY KEYWORDS ====================
EMERGENCY_KEYWORDS = [
    "can't breathe", "cannot breathe", "difficulty breathing",
    "chest pain", "heart attack", "stroke",
    "unconscious", "passed out", "suicide",
    "bleeding heavily", "severe pain", "emergency"
]

# ==================== SYSTEM PROMPT FOR GEMINI AI ====================
SYSTEM_PROMPT = """You are an AI Public Health Assistant for BMS Institute of Technology and Management.

Your role:
- Provide accurate, evidence-based health information
- Explain medical concepts in simple, understandable language
- Focus on disease prevention, symptoms, and general health guidance
- Be empathetic and supportive

Important guidelines:
- ALWAYS start responses with a brief, clear answer
- Use bullet points for lists
- Include relevant emojis for better readability
- Cite WHO, CDC, or similar authoritative sources when relevant
- For serious conditions, recommend consulting healthcare professionals

Topics you can help with:
- Disease information (symptoms, prevention, transmission)
- Health myths and facts
- General wellness and preventive care
- When to seek medical help
- Nutrition and exercise basics

What you CANNOT do:
- Diagnose diseases
- Prescribe medications
- Provide emergency medical care
- Replace professional medical advice

ALWAYS include this disclaimer for medical queries:
"⚠️ Remember: This is general information only. For medical diagnosis or treatment, please consult qualified healthcare professionals."

Format your responses clearly:
- Use **bold** for important terms
- Use bullet points (•) for lists
- Keep paragraphs short (2-3 sentences max)
- Use appropriate medical emojis (🏥💉🩺🦠)

Now, respond to the user's health question in a helpful, accurate, and caring manner."""

# ==================== AI RESPONSE FUNCTION ====================
def get_ai_response(user_message, conversation_history):
    """Generate intelligent response using Gemini AI or fallback to static responses"""
    
    message_lower = user_message.lower()
    
    # 1. EMERGENCY DETECTION (HIGHEST PRIORITY)
    if any(keyword in message_lower for keyword in EMERGENCY_KEYWORDS):
        return generate_emergency_response()
    
    # 2. USE GEMINI AI IF AVAILABLE
    if USE_AI:
        try:
            # Build conversation context
            context = SYSTEM_PROMPT + "\n\nConversation history:\n"
            
            # Add last 3 exchanges for context
            for exchange in conversation_history[-3:]:
                context += f"User: {exchange['user']}\n"
                context += f"Assistant: {exchange['bot']}\n"
            
            # Add current message
            context += f"\nUser's current question: {user_message}\n\nProvide a helpful, accurate response:"
            
            # Generate response with Gemini
            response = model.generate_content(context)
            
            # Extract text from response
            ai_response = response.text.strip()
            
            # Add disclaimer if discussing medical topics
            medical_keywords = ['symptom', 'disease', 'treatment', 'diagnose', 'medicine', 'medication']
            if any(keyword in message_lower for keyword in medical_keywords):
                if "⚠️" not in ai_response and "remember" not in ai_response.lower():
                    ai_response += "\n\n⚠️ **Remember:** This is general information only. For medical diagnosis or treatment, please consult qualified healthcare professionals."
            
            return ai_response
            
        except Exception as e:
            print(f"❌ Gemini AI Error: {str(e)}")
            print("⚠️ Falling back to static responses...")
            # Fall back to static responses
            return get_static_response(user_message, message_lower)
    
    # 3. FALLBACK TO STATIC RESPONSES
    return get_static_response(user_message, message_lower)


def get_static_response(user_message, message_lower):
    """Fallback static responses when AI is unavailable"""
    
    # Greeting
    if any(word in message_lower for word in ["hi", "hello", "hey"]) and len(message_lower.split()) < 5:
        return """Hello! 👋 Welcome to the AI Public Health Chatbot!

I can help you with:
✅ Disease information (COVID-19, Diabetes, TB, Malaria, Dengue, and more)
✅ Symptoms and prevention tips
✅ Health guidance and myth-busting
✅ Emergency guidance

💬 What would you like to know about today?"""
    
    # Check for specific diseases
    for disease_id, disease_info in DISEASES.items():
        if disease_id in message_lower or disease_info["name"].lower() in message_lower:
            symptoms_list = "\n• ".join(disease_info["symptoms"][:5])
            prevention_list = "\n• ".join(disease_info["prevention"][:4])
            
            return f"""**{disease_info['name']}**

📋 **What is it?**
{disease_info['description']}

🔍 **Common Symptoms:**
• {symptoms_list}

🛡️ **Prevention:**
• {prevention_list}

⚠️ **Remember:** For medical diagnosis or treatment, please consult healthcare professionals.

💬 Ask me more about symptoms, prevention, or other diseases!"""
    
    # Default response
    return """I can help with health information! 🏥

**Ask me about:**
• Disease information 
• Symptoms and prevention tips
• Health myths
• Emergency guidance

**Try asking:**
• "What are COVID-19 symptoms?"
• "How to prevent diabetes?"
• "Tell me about tuberculosis"

What would you like to know? 💙"""


def generate_emergency_response():
    """Generate emergency alert response"""
    return """🚨 **EMERGENCY ALERT** 🚨

This sounds like it may be a medical emergency!

**IMMEDIATE ACTIONS:**
📞 **Call emergency services NOW:**
   • India: 108 or 112
   • USA: 911
   • UK: 999 or 112

🏥 Go to the nearest emergency room immediately
⚕️ Don't wait - seek professional medical help

**Important:** This chatbot provides general information only and CANNOT replace emergency medical care. Your safety is the top priority!"""


# ==================== API ENDPOINTS ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'AI Public Health Chatbot API is running!',
        'ai_enabled': USE_AI,
        'ai_model': 'Gemini Pro' if USE_AI else 'Static responses',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat(),
        'diseases_loaded': len(DISEASES)
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint with AI integration"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default_session')
        
        if not user_message:
            return jsonify({
                'error': 'Message cannot be empty',
                'status': 'error'
            }), 400
        
        # Create session if doesn't exist
        if session_id not in sessions:
            sessions[session_id] = {
                'history': [],
                'created_at': datetime.now().isoformat()
            }
        
        # Generate AI response
        bot_response = get_ai_response(user_message, sessions[session_id]['history'])
        
        # Update conversation history
        sessions[session_id]['history'].append({
            'user': user_message,
            'bot': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 exchanges
        if len(sessions[session_id]['history']) > 10:
            sessions[session_id]['history'] = sessions[session_id]['history'][-10:]
        
        return jsonify({
            'response': bot_response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'ai_powered': USE_AI
        })
    
    except Exception as e:
        print(f"❌ Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'An error occurred processing your message',
            'details': str(e),
            'status': 'error'
        }), 500


@app.route('/api/clear-session', methods=['POST'])
def clear_session():
    """Clear conversation history"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default_session')
        
        if session_id in sessions:
            del sessions[session_id]
        
        return jsonify({
            'message': 'Session cleared successfully',
            'session_id': session_id,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get chatbot statistics"""
    try:
        total_sessions = len(sessions)
        total_messages = sum(len(session['history']) for session in sessions.values())
        
        return jsonify({
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'ai_enabled': USE_AI,
            'ai_model': 'Gemini Pro' if USE_AI else 'Static',
            'diseases_available': len(DISEASES),
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

# ============================================================================
# AUTHENTICATION ROUTES (Add this before if __name__)
# ============================================================================

# Simple user storage (in-memory - for demo only)
users = {}

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if email in users:
            return jsonify({'error': 'User already exists'}), 400
        
        # Store user (in production, hash the password!)
        users[email] = {
            'name': name,
            'email': email,
            'password': password  # DON'T do this in production!
        }
        
        return jsonify({
            'message': 'Registration successful',
            'user': {'name': name, 'email': email, 'id': email}
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if email not in users:
            return jsonify({'error': 'User not found'}), 404
        
        if users[email]['password'] != password:
            return jsonify({'error': 'Invalid password'}), 401
        
        user = users[email]
        return jsonify({
            'message': 'Login successful',
            'token': 'demo_token_' + email,  # In production, use JWT
            'user': {'name': user['name'], 'email': email, 'id': email}
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logout successful'}), 200
# ==================== RUN SERVER ====================
@app.route('/')
def root():
    return render_template('login.html')


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/app')
def app_page():
    return render_template('index1.html')

if __name__ == '__main__':
    print("=" * 70)
    print("🏥 AI-DRIVEN PUBLIC HEALTH CHATBOT - BACKEND SERVER v2.0")
    print("=" * 70)
    print(f"🤖 AI Status: {'✅ ENABLED (Gemini Pro)' if USE_AI else '⚠️ DISABLED (Static responses)'}")
    print(f"📊 Loaded {len(DISEASES)} diseases in knowledge base")
    print(f"🚨 Monitoring {len(EMERGENCY_KEYWORDS)} emergency keywords")
    print("=" * 70)
    print("🌐 Server starting on http://localhost:5000")
    print("📡 API Endpoints:")
    print("   • GET  /health - Health check")
    print("   • POST /api/chat - Main chat endpoint (AI-powered)")
    print("   • POST /api/clear-session - Clear session")
    print("   • GET  /api/stats - Server statistics")
    print("=" * 70)
    
    if not USE_AI:
        print("⚠️  WARNING: Running without AI integration!")
        print("⚠️  Please add GEMINI_API_KEY to .env file for full functionality")
        print("=" * 70)
    
    print("✅ Ready for connections!")
    print("=" * 70)
    
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
