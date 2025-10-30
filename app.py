"""
AI-Driven Public Health Chatbot - Backend
BMS Institute of Technology and Management
Team: Adarshini (Backend), Bhoomi (Frontend), Jyoti (UI/UX), Navya (Data)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import re

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend connection

# In-memory session storage (for prototype)
sessions = {}

# ==================== DISEASE KNOWLEDGE BASE ====================
# Navya: Add your disease data here
DISEASES = {
    "covid-19": {
        "name": "COVID-19",
        "description": "COVID-19 is a respiratory illness caused by the SARS-CoV-2 virus. It spreads easily from person to person and can cause mild to severe illness.",
        "symptoms": [
            "Fever or chills",
            "Cough (usually dry)",
            "Shortness of breath or difficulty breathing",
            "Fatigue and body aches",
            "Loss of taste or smell",
            "Sore throat",
            "Congestion or runny nose",
            "Headache",
            "Nausea or vomiting",
            "Diarrhea"
        ],
        "prevention": [
            "Get vaccinated and stay up to date with booster shots",
            "Wear a well-fitted mask in crowded indoor settings",
            "Maintain physical distance (at least 6 feet) from others",
            "Wash hands frequently with soap and water for 20 seconds",
            "Use hand sanitizer with at least 60% alcohol",
            "Avoid touching your eyes, nose, and mouth",
            "Stay home if you feel sick",
            "Cover coughs and sneezes with your elbow",
            "Clean and disinfect frequently touched surfaces"
        ],
        "transmission": "COVID-19 spreads primarily through respiratory droplets when an infected person coughs, sneezes, talks, or breathes. It can also spread by touching contaminated surfaces and then touching your face.",
        "emergency_signs": [
            "Difficulty breathing or shortness of breath",
            "Persistent chest pain or pressure",
            "New confusion or inability to wake up",
            "Bluish lips or face",
            "Severe, persistent dizziness"
        ],
        "treatment_approach": "Most cases can be managed at home with rest, fluids, and over-the-counter medications. Severe cases require hospitalization. Consult a healthcare provider for proper evaluation."
    },
    "diabetes": {
        "name": "Diabetes",
        "description": "Diabetes is a chronic disease that occurs when blood glucose (blood sugar) levels are too high. It affects how your body processes food for energy.",
        "symptoms": [
            "Increased thirst and frequent urination",
            "Extreme hunger",
            "Unexplained weight loss",
            "Fatigue and weakness",
            "Blurred vision",
            "Slow-healing sores or frequent infections",
            "Tingling or numbness in hands or feet",
            "Darkened skin in armpits or neck"
        ],
        "prevention": [
            "Maintain a healthy weight through diet and exercise",
            "Be physically active for at least 30 minutes daily",
            "Eat a balanced diet rich in fruits, vegetables, and whole grains",
            "Limit sugar and refined carbohydrates",
            "Choose lean proteins and healthy fats",
            "Don't smoke",
            "Limit alcohol consumption",
            "Get regular health screenings",
            "Manage stress through relaxation techniques"
        ],
        "transmission": "Diabetes is not contagious. It develops due to genetic factors, lifestyle choices, and other health conditions. Type 1 is an autoimmune condition, while Type 2 is often related to lifestyle and genetics.",
        "emergency_signs": [
            "Blood sugar over 240 mg/dL with ketones",
            "Blood sugar below 70 mg/dL with confusion",
            "Severe confusion or loss of consciousness",
            "Difficulty breathing",
            "Fruity-smelling breath"
        ],
        "treatment_approach": "Management includes blood sugar monitoring, healthy eating, regular exercise, and medication as prescribed. Type 1 requires insulin; Type 2 may be managed with lifestyle changes and/or medication."
    },
    "tuberculosis": {
        "name": "Tuberculosis (TB)",
        "description": "TB is a bacterial infection caused by Mycobacterium tuberculosis that primarily affects the lungs but can affect other parts of the body.",
        "symptoms": [
            "Persistent cough lasting 3+ weeks",
            "Coughing up blood or mucus",
            "Chest pain when breathing or coughing",
            "Unintentional weight loss",
            "Fatigue and weakness",
            "Fever and chills",
            "Night sweats",
            "Loss of appetite"
        ],
        "prevention": [
            "Get vaccinated with BCG vaccine (in endemic areas)",
            "Avoid close contact with TB patients during active disease",
            "Ensure good ventilation in living and working spaces",
            "Cover your mouth when coughing or sneezing",
            "Complete the full course of treatment if infected",
            "Get tested regularly if you're at high risk",
            "Wear masks in healthcare settings",
            "Strengthen immune system through healthy living"
        ],
        "transmission": "TB spreads through the air when a person with active TB disease coughs, sneezes, speaks, or sings. It requires prolonged close contact for transmission.",
        "emergency_signs": [
            "Coughing up large amounts of blood",
            "Severe breathing difficulty",
            "Chest pain with high fever",
            "Confusion or altered mental state"
        ],
        "treatment_approach": "TB is curable with a 6-9 month course of antibiotics. It's crucial to complete the entire treatment even if symptoms improve. Drug-resistant TB requires longer treatment with special medications."
    },
    "malaria": {
        "name": "Malaria",
        "description": "Malaria is a life-threatening disease caused by Plasmodium parasites transmitted through the bites of infected female Anopheles mosquitoes.",
        "symptoms": [
            "High fever (can spike to 104°F/40°C)",
            "Chills and shaking",
            "Severe headache",
            "Nausea and vomiting",
            "Muscle pain and fatigue",
            "Sweating",
            "Abdominal pain",
            "Diarrhea"
        ],
        "prevention": [
            "Use insecticide-treated bed nets while sleeping",
            "Apply mosquito repellent on exposed skin",
            "Wear long-sleeved shirts and long pants, especially at dawn and dusk",
            "Use indoor insecticide sprays or coils",
            "Take antimalarial medication when traveling to endemic areas",
            "Install screens on windows and doors",
            "Eliminate standing water where mosquitoes breed",
            "Use air conditioning when available"
        ],
        "transmission": "Malaria is transmitted by the bite of infected Anopheles mosquitoes, which are most active between dusk and dawn. It cannot spread directly from person to person.",
        "emergency_signs": [
            "Severe headache with confusion",
            "Convulsions or seizures",
            "Difficulty breathing",
            "Severe anemia (pale skin, weakness)",
            "Yellow discoloration of skin and eyes",
            "Kidney failure"
        ],
        "treatment_approach": "Malaria requires immediate medical treatment with antimalarial drugs. The specific medication depends on the type of malaria parasite and severity of disease. Early treatment is crucial."
    },
    "dengue": {
        "name": "Dengue Fever",
        "description": "Dengue is a mosquito-borne viral infection that causes severe flu-like illness and can develop into severe dengue (dengue hemorrhagic fever), which can be life-threatening.",
        "symptoms": [
            "High fever (104°F/40°C)",
            "Severe headache",
            "Pain behind the eyes",
            "Severe joint and muscle pain",
            "Nausea and vomiting",
            "Skin rash (appears 2-5 days after fever)",
            "Mild bleeding (nose, gums, or easy bruising)",
            "Fatigue"
        ],
        "prevention": [
            "Use mosquito repellent regularly",
            "Wear long-sleeved clothing and long pants",
            "Use mosquito nets, especially during daytime",
            "Install window and door screens",
            "Remove standing water from containers, flower pots, and tires",
            "Empty and clean water storage containers weekly",
            "Use mosquito coils or vaporizers",
            "Cover water storage containers"
        ],
        "transmission": "Dengue is transmitted by Aedes mosquitoes, primarily Aedes aegypti. These mosquitoes bite during daytime, especially early morning and before dusk. Cannot spread person to person.",
        "emergency_signs": [
            "Severe abdominal pain",
            "Persistent vomiting",
            "Bleeding from nose or gums",
            "Blood in vomit or stool",
            "Difficulty breathing or rapid breathing",
            "Cold or clammy skin",
            "Severe weakness"
        ],
        "treatment_approach": "No specific treatment for dengue. Focus on rest, staying hydrated, and managing symptoms with acetaminophen (avoid aspirin and ibuprofen). Severe dengue requires hospitalization for IV fluids and monitoring."
    },
    "influenza": {
        "name": "Influenza (Flu)",
        "description": "Influenza is a contagious respiratory illness caused by influenza viruses that infect the nose, throat, and sometimes the lungs.",
        "symptoms": [
            "Fever",
            "Chills",
            "Cough",
            "Sore throat",
            "Runny or stuffy nose",
            "Muscle or body aches",
            "Fatigue"
        ],
        "prevention": [
            "Annual flu vaccination",
            "Frequent hand washing",
            "Avoid close contact with sick individuals",
            "Cover mouth and nose when coughing or sneezing"
        ],
        "myths": [
            "Flu vaccine can give you the flu",
            "The flu is just a bad cold",
            "Only sick people spread flu",
            "You don't need a flu shot every year"
        ],
        "transmission": "Influenza spreads mainly through droplets made when people with flu cough, sneeze, or talk.",
        "treatment_approach": "Rest, hydration, and antiviral drugs (if prescribed). Seek medical attention for severe symptoms."
    },
    "hypertension": {
        "name": "Hypertension (High Blood Pressure)",
        "description": "Hypertension is a condition where the force of the blood against the artery walls is consistently too high, increasing the risk of heart disease and stroke.",
        "symptoms": [
            "Often asymptomatic",
            "Headaches",
            "Dizziness",
            "Chest pain",
            "Shortness of breath"
        ],
        "prevention": [
            "Maintain a healthy diet and weight",
            "Exercise regularly",
            "Limit salt and alcohol intake",
            "Quit smoking",
            "Manage stress",
            "Regular blood pressure checkups"
        ],
        "myths": [
            "Only older people get hypertension",
            "You can control salt intake just by avoiding table salt",
            "High blood pressure cannot be prevented"
        ],
        "transmission": "Hypertension is not contagious. It develops due to lifestyle, genetics, and health conditions.",
        "treatment_approach": "Lifestyle modifications, medication as prescribed, and regular monitoring."
    },
    "asthma": {
        "name": "Asthma",
        "description": "Asthma is a chronic condition that affects the airways in the lungs, making it difficult to breathe.",
        "symptoms": [
            "Wheezing",
            "Coughing",
            "Shortness of breath",
            "Chest tightness"
        ],
        "prevention": [
            "Avoid known triggers",
            "Take prescribed inhalers regularly",
            "Avoid smoking",
            "Manage allergies",
            "Schedule regular checkups"
        ],
        "myths": [
            "Only children get asthma",
            "You shouldn’t exercise if you have asthma",
            "No wheezing means no asthma",
            "Removing milk or wheat will cure asthma"
        ],
        "transmission": "Asthma is not contagious but can be triggered by environmental or genetic factors.",
        "treatment_approach": "Inhalers, medication, and trigger avoidance."
    },
    "typhoid": {
        "name": "Typhoid Fever",
        "description": "Typhoid fever is a bacterial infection caused by Salmonella Typhi, spread through contaminated food and water.",
        "symptoms": [
            "Fever",
            "Headache",
            "Abdominal pain",
            "Constipation or diarrhea",
            "Fatigue"
        ],
        "prevention": [
            "Vaccination",
            "Drink safe and clean water",
            "Practice good food hygiene",
            "Wash hands regularly"
        ],
        "myths": [
            "Typhoid can be cured without antibiotics",
            "Immunity after infection protects for life",
            "Typhoid spreads by coughing or sneezing"
        ],
        "transmission": "Typhoid spreads through ingestion of food or water contaminated with the feces of an infected person.",
        "treatment_approach": "Antibiotic treatment and hydration. Avoid self-medication."
    },
    "measles": {
        "name": "Measles",
        "description": "Measles is a highly contagious viral infection that causes fever, rash, and respiratory symptoms.",
        "symptoms": [
            "Rash",
            "High fever",
            "Cough",
            "Runny nose",
            "Red eyes",
            "Koplik spots (inside mouth)"
        ],
        "prevention": [
            "Two doses of MMR vaccine",
            "Avoid contact with infected individuals"
        ],
        "myths": [
            "Only children get measles",
            "Measles isn’t serious",
            "Hand washing alone can prevent measles",
            "Vaccine isn’t needed"
        ],
        "transmission": "Measles spreads through respiratory droplets from coughs and sneezes.",
        "treatment_approach": "No specific antiviral treatment. Supportive care with fluids, rest, and vitamin A supplements."
    },
    "pneumonia": {
        "name": "Pneumonia",
        "description": "Pneumonia is an infection that inflames the air sacs in one or both lungs, which may fill with fluid.",
        "symptoms": [
            "Cough (sometimes with phlegm)",
            "Chest pain",
            "Difficulty breathing",
            "Fever",
            "Fatigue"
        ],
        "prevention": [
            "Vaccinations (flu, pneumococcal)",
            "Good hand hygiene",
            "Avoid smoking",
            "Seek prompt treatment for respiratory infections"
        ],
        "myths": [
            "Pneumonia is just a bad cold",
            "Only elderly and children get pneumonia",
            "Pneumonia is only caused by bacteria",
            "Recovery is always quick"
        ],
        "transmission": "Pneumonia spreads through airborne droplets from coughs or sneezes and via contaminated surfaces.",
        "treatment_approach": "Antibiotics (if bacterial), rest, and fluids. Hospital care for severe cases."
    },
    "hepatitis": {
        "name": "Hepatitis",
        "description": "Hepatitis is inflammation of the liver caused by viral infections, toxins, or autoimmune diseases.",
        "symptoms": [
            "Often asymptomatic initially",
            "Jaundice",
            "Fatigue",
            "Dark urine",
            "Abdominal pain"
        ],
        "prevention": [
            "Vaccination for hepatitis A and B",
            "Avoid sharing needles or personal items",
            "Ensure safe food and water",
            "Regular health checkups"
        ],
        "myths": [
            "Only alcoholics or drug abusers get hepatitis",
            "Hepatitis only affects poor countries",
            "You can identify hepatitis by symptoms",
            "No cure for hepatitis"
        ],
        "transmission": "Hepatitis spreads through contact with infected blood, bodily fluids, or contaminated food/water.",
        "treatment_approach": "Depends on type — may include antiviral medication, rest, and liver support."
    },
    "chickenpox": {
        "name": "Chickenpox (Varicella)",
        "description": "Chickenpox is a highly contagious viral infection causing an itchy, blister-like rash.",
        "symptoms": [
            "Fever",
            "Fatigue",
            "Headache",
            "Itchy blister rash",
            "Loss of appetite"
        ],
        "prevention": [
            "Two-dose varicella vaccine",
            "Avoid contact with infected individuals",
            "Maintain good hygiene",
            "Do not share personal items"
        ],
        "myths": [
            "Chickenpox parties are safe",
            "Vaccine is unnecessary",
            "Only children get chickenpox"
        ],
        "transmission": "Spreads easily through airborne droplets or contact with the rash.",
        "treatment_approach": "Rest, fluids, calamine lotion, and antiviral medication (if prescribed). Avoid scratching to prevent infection."
    },

}

# ==================== HEALTH MYTHS DATABASE ====================
# Navya: Add more health myths here
MYTHS = {
    "5g": "FALSE: 5G networks do NOT cause or spread COVID-19. Viruses cannot travel through radio waves or mobile networks. COVID-19 spreads through respiratory droplets.",
    "hot water": "FALSE: Drinking hot water does not prevent or cure COVID-19. While staying hydrated is important, hot water cannot kill the virus. Vaccination and preventive measures are effective.",
    "antibiotics virus": "FALSE: Antibiotics do NOT work against viruses, including COVID-19, flu, or colds. Antibiotics only work against bacterial infections. Using antibiotics unnecessarily can lead to resistance.",
    "sugar diabetes": "PARTIALLY FALSE: Eating sugar alone doesn't directly cause diabetes. However, consuming too much sugar can lead to weight gain and obesity, which are risk factors for Type 2 diabetes.",
    "tb hereditary": "FALSE: TB is NOT hereditary or genetic. It's caused by bacteria and spreads through the air. However, some people may have genetic factors that affect their immune response to TB.",
    "cold weather sick": "FALSE: Cold weather itself doesn't make you sick. Viruses cause colds and flu. However, people tend to stay indoors more in cold weather, which can increase virus transmission.",
    "vitamin c cure": "FALSE: While vitamin C supports immune function, it cannot prevent or cure COVID-19 or other viral infections. A balanced diet is important, but it's not a substitute for vaccination.",
    "hand dryers kill virus": "FALSE: Hand dryers do NOT kill viruses. Proper handwashing with soap and water for 20 seconds is effective. Hand dryers are only for drying hands after washing."
    "flu vaccine": "FALSE: The flu vaccine cannot give you the flu. It helps your body build immunity against influenza viruses.",
    "blood pressure salt": "FALSE: Avoiding only table salt is not enough. Processed foods also contribute to high sodium intake.",
    "exercise asthma": "FALSE: Exercise can actually improve lung function when asthma is well controlled.",
    "typhoid cure": "FALSE: Typhoid requires antibiotics; untreated infections can become severe.",
    "measles vaccine": "FALSE: The MMR vaccine is essential and safe. It prevents measles and its complications.",
    "pneumonia cold": "FALSE: Pneumonia is more serious than a cold and can be caused by bacteria, viruses, or fungi.",
    "hepatitis alcoholics": "FALSE: Anyone can get hepatitis through viruses or unsafe practices.",
    "chickenpox parties": "FALSE: Chickenpox parties are dangerous and can cause severe infections. Vaccination is safer."
}

# ==================== EMERGENCY KEYWORDS ====================
EMERGENCY_KEYWORDS = [
    "can't breathe", "cannot breathe", "difficulty breathing", "hard to breathe",
    "chest pain", "heart attack", "stroke",
    "unconscious", "passed out", "fainted",
    "suicide", "kill myself", "end my life",
    "bleeding heavily", "losing blood",
    "severe pain", "extreme pain",
    "emergency", "urgent", "critical",
    "overdose", "poisoned",
    "seizure", "convulsion"
]

# ==================== AI RESPONSE LOGIC ====================
def get_ai_response(user_message, conversation_history):
    """
    The brain of the chatbot - generates intelligent responses
    Adarshini: This is your main AI logic function
    """
    message_lower = user_message.lower()
    
    # ===== 1. EMERGENCY DETECTION (HIGHEST PRIORITY) =====
    if any(keyword in message_lower for keyword in EMERGENCY_KEYWORDS):
        return generate_emergency_response()
    
    # ===== 2. GREETING DETECTION =====
    greeting_words = ["hi", "hello", "hey", "namaste", "good morning", "good evening", "greetings"]
    if any(word in message_lower for word in greeting_words) and len(message_lower.split()) < 5:
        return generate_greeting_response()
    
    # ===== 3. MYTH BUSTING =====
    for myth_key, myth_answer in MYTHS.items():
        if myth_key in message_lower:
            return f"""🔍 **MYTH CHECK**

{myth_answer}

💡 **Remember:** Always verify health information from reliable sources:
• World Health Organization (WHO)
• Centers for Disease Control (CDC)
• National Health Portal

❓ Have more questions? I'm here to help with accurate information!"""
    
    # ===== 4. DISEASE INFORMATION QUERIES =====
    for disease_id, disease_info in DISEASES.items():
        disease_name_lower = disease_info["name"].lower()
        
        # Check if user is asking about this disease
        if disease_id in message_lower or disease_name_lower in message_lower or any(word in disease_id for word in message_lower.split()):
            
            # Check what specific information user wants
            if any(word in message_lower for word in ["symptom", "sign", "feel", "experience"]):
                return generate_symptom_response(disease_info)
            
            elif any(word in message_lower for word in ["prevent", "avoid", "protection", "stop", "reduce risk"]):
                return generate_prevention_response(disease_info)
            
            elif any(word in message_lower for word in ["spread", "transmit", "contagious", "catch", "get"]):
                return generate_transmission_response(disease_info)
            
            elif any(word in message_lower for word in ["treat", "cure", "medicine", "medication"]):
                return generate_treatment_response(disease_info)
            
            elif any(word in message_lower for word in ["emergency", "danger", "serious", "when to see doctor"]):
                return generate_emergency_info_response(disease_info)
            
            else:
                # General information about the disease
                return generate_general_info_response(disease_info)
    
    # ===== 5. GENERAL HEALTH QUERIES =====
    if any(word in message_lower for word in ["disease", "illness", "sick", "health", "medical"]):
        return generate_disease_list_response()
    
    # ===== 6. HELP / CAPABILITIES =====
    if any(word in message_lower for word in ["help", "what can you do", "capabilities", "features"]):
        return generate_help_response()
    
    # ===== 7. THANK YOU =====
    if any(word in message_lower for word in ["thank", "thanks", "appreciate"]):
        return """You're welcome! 😊

I'm here to help you stay informed about health topics.

Feel free to ask me anything about:
• Disease information
• Prevention tips
• Symptoms
• Health myths

Stay healthy! 🏥"""
    
    # ===== 8. GOODBYE =====
    if any(word in message_lower for word in ["bye", "goodbye", "see you", "exit", "quit"]):
        return """Goodbye! Take care of your health! 👋

Remember:
• Prevention is better than cure
• Stay informed with accurate information
• Consult healthcare professionals when needed

Feel free to return anytime you have health questions! 🏥"""
    
    # ===== 9. DEFAULT RESPONSE =====
    return generate_default_response()

# ==================== RESPONSE GENERATORS ====================

def generate_emergency_response():
    """Generate emergency alert response"""
    return """🚨 **EMERGENCY ALERT** 🚨

This sounds like it may be a medical emergency!

**IMMEDIATE ACTIONS:**
📞 Call emergency services NOW:
   • India: 108 or 112
   • USA: 911
   • UK: 999 or 112
   • EU: 112

🏥 Go to the nearest emergency room
⚕️ Don't wait - seek professional medical help immediately

**Important:** This chatbot provides general information only and cannot replace emergency medical care. Your safety is the top priority!"""

def generate_greeting_response():
    """Generate friendly greeting"""
    return """Hello! 👋 Welcome to the **AI Public Health Chatbot**!

I'm here to help you with:
✅ Disease information (COVID-19, Diabetes, TB, Malaria, Dengue, and more)
✅ Symptoms and prevention tips
✅ Health guidance and myth-busting
✅ Emergency guidance

⚠️ **Important Disclaimer:** I provide general health information only. For medical diagnosis, treatment, or emergencies, please consult qualified healthcare professionals.

💬 What would you like to know about today?"""

def generate_symptom_response(disease_info):
    """Generate response about symptoms"""
    symptoms_list = "\n• ".join(disease_info["symptoms"])
    
    response = f"""**{disease_info['name']} - Common Symptoms**

🔍 **Symptoms to watch for:**
• {symptoms_list}

⚠️ **Important Notes:**
• Symptoms can vary from person to person
• Some people may experience only mild symptoms
• If you experience these symptoms, consult a healthcare provider

"""
    
    if "emergency_signs" in disease_info and disease_info["emergency_signs"]:
        emergency_list = "\n• ".join(disease_info["emergency_signs"])
        response += f"""🚨 **SEEK EMERGENCY CARE IMMEDIATELY IF:**
• {emergency_list}

"""
    
    response += """💡 **Remember:** This is general information. Only a healthcare professional can provide a proper diagnosis.

Need more information about prevention or treatment?"""
    
    return response

def generate_prevention_response(disease_info):
    """Generate response about prevention"""
    prevention_list = "\n• ".join(disease_info["prevention"])
    
    return f"""**{disease_info['name']} - Prevention Tips**

🛡️ **How to protect yourself:**
• {prevention_list}

✅ **Key Takeaway:** Prevention is always better than cure!

💡 **Pro Tip:** Combine multiple prevention strategies for the best protection.

Would you like to know more about symptoms or transmission?"""

def generate_transmission_response(disease_info):
    """Generate response about transmission"""
    return f"""**{disease_info['name']} - How It Spreads**

📢 **Transmission Information:**
{disease_info['transmission']}

🛡️ **Prevention Tip:** Understanding how a disease spreads helps you take appropriate precautions to protect yourself and others.

Would you like to know about prevention methods?"""

def generate_treatment_response(disease_info):
    """Generate response about treatment"""
    return f"""**{disease_info['name']} - Treatment Approach**

💊 **General Treatment Information:**
{disease_info['treatment_approach']}

⚠️ **IMPORTANT DISCLAIMER:**
• This chatbot does NOT provide medical advice or prescribe treatments
• Always consult a qualified healthcare provider for diagnosis and treatment
• Do not self-medicate based on online information
• Follow your doctor's recommendations

🏥 For proper medical care, please visit a healthcare facility or consult your doctor.

Need information about symptoms or prevention?"""

def generate_emergency_info_response(disease_info):
    """Generate response about emergency signs"""
    if "emergency_signs" in disease_info and disease_info["emergency_signs"]:
        emergency_list = "\n• ".join(disease_info["emergency_signs"])
        
        return f"""**{disease_info['name']} - Emergency Warning Signs**

🚨 **SEEK IMMEDIATE MEDICAL ATTENTION IF YOU EXPERIENCE:**
• {emergency_list}

📞 **Emergency Actions:**
• Call emergency services: 108 (India) / 911 (USA) / 112 (EU)
• Go to nearest emergency room
• Do not delay seeking help

⏰ **Time is Critical:** Early medical intervention can save lives!

💡 For general symptoms and prevention, feel free to ask!"""
    else:
        return f"""For emergency situations related to {disease_info['name']}, please consult a healthcare provider immediately or call emergency services.

Would you like to know about general symptoms or prevention?"""

def generate_general_info_response(disease_info):
    """Generate comprehensive disease information"""
    symptoms_list = "\n• ".join(disease_info["symptoms"][:5])  # Show first 5 symptoms
    prevention_list = "\n• ".join(disease_info["prevention"][:5])  # Show first 5 prevention tips
    
    return f"""**{disease_info['name']}**

📋 **What is it?**
{disease_info['description']}

🔍 **Common Symptoms:**
• {symptoms_list}
{f"• ...and {len(disease_info['symptoms']) - 5} more" if len(disease_info['symptoms']) > 5 else ""}

🛡️ **Prevention:**
• {prevention_list}
{f"• ...and {len(disease_info['prevention']) - 5} more" if len(disease_info['prevention']) > 5 else ""}

📢 **How it spreads:**
{disease_info['transmission']}

💡 **Want more details?** Ask me about:
• Specific symptoms
• Complete prevention methods
• Treatment approach
• Emergency warning signs"""

def generate_disease_list_response():
    """Show available diseases"""
    disease_list = "\n• ".join([f"{info['name']}" for info in DISEASES.values()])
    
    return f"""**Available Disease Information** 🏥

I can provide detailed information about:
• {disease_list}

**What I can tell you:**
✅ Symptoms and signs
✅ Prevention tips
✅ How diseases spread
✅ When to seek medical help
✅ General treatment approaches

💬 **Try asking:**
• "What are COVID-19 symptoms?"
• "How to prevent diabetes?"
• "How does TB spread?"
• "Tell me about malaria"

What would you like to know?"""

def generate_help_response():
    """Show chatbot capabilities"""
    return """**How I Can Help You** 🤖

I'm your AI Public Health Assistant! Here's what I can do:

**📚 Disease Information:**
• Symptoms and warning signs
• Prevention tips and guidelines
• How diseases spread
• When to seek medical help

**🔍 Myth-Busting:**
• Correct common health misconceptions
• Provide fact-based information
• Fight misinformation

**🚨 Emergency Guidance:**
• Recognize emergency situations
• Provide emergency contact information
• Direct to appropriate help

**✅ Covered Topics:**
• COVID-19
• Diabetes
• Tuberculosis (TB)
• Malaria
• Dengue Fever
• General health guidance

**⚠️ What I CANNOT Do:**
❌ Diagnose diseases
❌ Prescribe medications
❌ Replace doctor consultations
❌ Provide emergency medical care

💬 **Just ask me anything about health topics!**"""

def generate_default_response():
    """Default fallback response"""
    return """I'm here to help with health information! 🏥

**I can assist you with:**
• Disease information (COVID-19, Diabetes, TB, Malaria, Dengue)
• Symptoms and prevention tips
• How diseases spread
• Health myth-busting
• Emergency guidance

**Try asking:**
• "What are the symptoms of COVID-19?"
• "How can I prevent diabetes?"
• "Tell me about tuberculosis"
• "Does 5G cause COVID-19?" (myth-busting)

⚠️ **Remember:** I provide general information only. For medical diagnosis or treatment, please consult healthcare professionals.

What would you like to know?"""

# ==================== API ENDPOINTS ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint - verify server is running"""
    return jsonify({
        'status': 'healthy',
        'message': 'AI Public Health Chatbot API is running!',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'diseases_loaded': len(DISEASES),
        'myths_loaded': len(MYTHS)
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint - handles user messages
    Accepts: {"message": "user question", "session_id": "unique_id"}
    Returns: {"response": "bot answer", "session_id": "unique_id", "timestamp": "..."}
    """
    try:
        # Get request data
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default_session')
        
        # Validate message
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
        
        # Keep only last 10 exchanges for memory management
        if len(sessions[session_id]['history']) > 10:
            sessions[session_id]['history'] = sessions[session_id]['history'][-10:]
        
        # Return response
        return jsonify({
            'response': bot_response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'An error occurred processing your message',
            'details': str(e),
            'status': 'error'
        }), 500

@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    """Get list of all available diseases"""
    try:
        disease_list = [
            {
                'id': disease_id,
                'name': info['name'],
                'description': info['description'][:100] + '...'  # Short preview
            }
            for disease_id, info in DISEASES.items()
        ]
        
        return jsonify({
            'diseases': disease_list,
            'count': len(disease_list),
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/disease/<disease_id>', methods=['GET'])
def get_disease_detail(disease_id):
    """Get detailed information about specific disease"""
    try:
        disease_id_lower = disease_id.lower().replace(' ', '-')
        
        if disease_id_lower in DISEASES:
            return jsonify({
                'disease': DISEASES[disease_id_lower],
                'status': 'success'
            })
        else:
            return jsonify({
                'error': 'Disease not found',
                'available_diseases': list(DISEASES.keys()),
                'status': 'error'
            }), 404
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/clear-session', methods=['POST'])
def clear_session():
    """Clear conversation history for a session"""
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
            'diseases_available': len(DISEASES),
            'myths_available': len(MYTHS),
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

# ==================== RUN SERVER ====================
if __name__ == '__main__':
    print("=" * 70)
    print("🏥 AI-DRIVEN PUBLIC HEALTH CHATBOT - BACKEND SERVER")
    print("=" * 70)
    print(f"📊 Loaded {len(DISEASES)} diseases: {', '.join([d['name'] for d in DISEASES.values()])}")
    print(f"🔍 Loaded {len(MYTHS)} health myths")
    print(f"🚨 Monitoring {len(EMERGENCY_KEYWORDS)} emergency keywords")
    print("=" * 70)
    print("🌐 Server starting on http://localhost:5000")
    print("📡 API Endpoints:")
    print("   • GET  /health - Health check")
    print("   • POST /api/chat - Main chat endpoint")
    print("   • GET  /api/diseases - List diseases")
    print("   • GET  /api/disease/<id> - Disease details")
    print("   • POST /api/clear-session - Clear session")
    print("   • GET  /api/stats - Server statistics")
    print("=" * 70)
    print("✅ Ready for connections from frontend!")
    print("=" * 70)
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
