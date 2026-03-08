package com.medtriage.app.ui.utils

import androidx.compose.runtime.Composable

object Translator {
    
    // Fallback if translation is missing
    fun t(englishText: String, langCode: String): String {
        if (langCode == "en") return englishText
        
        val dict = DICTIONARY[englishText]
        return dict?.get(langCode) ?: englishText
    }

    // A lightweight dictionary for hackathon purposes.
    // Core structural UI elements only.
    val DICTIONARY = mapOf(
        "Select Your Role" to mapOf(
            "hi" to "अपनी भूमिका चुनें",
            "ta" to "உங்கள் பங்கைத் தேர்ந்தெடுக்கவும்",
            "te" to "మీ పాత్రను ఎంచుకోండి",
            "kn" to "ನಿಮ್ಮ ಪಾತ್ರವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
            "ml" to "നിങ്ങളുടെ റോൾ തിരഞ്ഞെടുക്കുക",
            "bn" to "আপনার ভূমিকা নির্বাচন করুন"
        ),
        "Healthcare Worker" to mapOf(
            "hi" to "स्वास्थ्य कार्यकर्ता",
            "ta" to "சுகாதாரப் பணியாளர்",
            "te" to "ఆరోగ్య కార్యకర్త",
            "kn" to "ಆರೋಗ್ಯ ಕಾರ್ಯಕರ್ತ",
            "ml" to "ആരോഗ്യ പ്രവർത്തകൻ",
            "bn" to "স্বাস্থ্যকর্মী"
        ),
        "RMP, Nurse, or Medical Professional" to mapOf(
            "hi" to "आरएमपी, नर्स, या चिकित्सा पेशेवर",
            "ta" to "RMP, செவிலியர் அல்லது மருத்துவ நிபுணர்",
            "te" to "RMP, నర్సు లేదా వైద్య నిపుణుడు",
            "kn" to "RMP, ನರ್ಸ್ ಅಥವಾ ವೈದ್ಯಕೀಯ ವೃತ್ತಿಪರ",
            "ml" to "RMP, നഴ്സ് അല്ലെങ്കിൽ മെഡിക്കൽ പ്രൊഫഷണൽ",
            "bn" to "আরএমপি, নার্স বা চিকিৎসা পেশাদার"
        ),
        "Patient / User" to mapOf(
            "hi" to "रोगी / उपयोगकर्ता",
            "ta" to "நோயாளி / பயனர்",
            "te" to "రోగి / వినియోగదారు",
            "kn" to "ರೋಗಿ / ಬಳಕೆದಾರ",
            "ml" to "രോഗി / ഉപയോക്താവ്",
            "bn" to "রোগী / ব্যবহারকারী"
        ),
        "Request medical assistance" to mapOf(
            "hi" to "चिकित्सा सहायता का अनुरोध करें",
            "ta" to "மருத்துவ உதவியைக் கோருங்கள்",
            "te" to "వైద్య సహాయం అభ్యర్థించండి",
            "kn" to "ವೈದ್ಯಕೀಯ ನೆರವು ವಿನಂತಿಸಿ",
            "ml" to "മെഡിക്കൽ സഹായം അഭ്യർത്ഥിക്കുക",
            "bn" to "চিকিৎসা সহায়তার অনুরোধ করুন"
        ),
        "Language / भाषा" to mapOf(
            "hi" to "Language / भाषा",
            "ta" to "மொழி / Language",
            "te" to "భాష / Language",
            "kn" to "ಭಾಷೆ / Language",
            "ml" to "ഭാഷ / Language",
            "bn" to "ভাষা / Language"
        ),
        "Your selection will determine your access level" to mapOf(
            "hi" to "आपका चयन आपके पहुँच स्तर को निर्धारित करेगा",
            "ta" to "உங்கள் தேர்வு உங்கள் அணுகல் நிலையைக் குறிக்கும்",
            "te" to "మీ ఎంపిక మీ యాక్సెస్ స్థాయిని నిర్ణయిస్తుంది",
            "kn" to "ನಿಮ್ಮ ಆಯ್ಕೆಯು ನಿಮ್ಮ ಪ್ರವೇಶ ಮಟ್ಟವನ್ನು ನಿರ್ಧರಿಸುತ್ತದೆ",
            "ml" to "നിങ്ങളുടെ തിരഞ്ഞെടുപ്പ് നിങ്ങളുടെ ആക്സസ് നില തീരുമാനിക്കും",
            "bn" to "আপনার নির্বাচন আপনার অ্যাক্সেস স্তর নির্ধারণ করবে"
        ),
        "Start new triage assessment" to mapOf(
            "hi" to "नया ट्राइएज मूल्यांकन शुरू करें",
            "ta" to "புதிய ட்ரையேஜ் மதிப்பீட்டைத் தொடங்குங்கள்",
            "te" to "కొత్త ట్రయాజ్ అంచనను ప్రారంభించండి",
            "kn" to "ಹೊಸ ಟ್ರಯಾಜ್ ಮೌಲ್ಯಮಾಪನವನ್ನು ಪ್ರಾರಂಭಿಸಿ",
            "ml" to "പുതിയ ട്രയേജ് വിലയിരുത്തൽ ആരംഭിക്കുക",
            "bn" to "নতুন ট্রায়াজ মূল্যায়ন শুরু করুন"
        ),
        "Start" to mapOf(
            "hi" to "शुरू करें",
            "ta" to "தொடங்கு",
            "te" to "ప్రారంభించు",
            "kn" to "ಪ್ರಾರಂಭಿಸಿ",
            "ml" to "തുടങ്ങുക",
            "bn" to "শুরু করুন"
        ),
        "Sign In" to mapOf(
            "hi" to "साइन इन करें",
            "ta" to "உள்நுழைக",
            "te" to "సైన్ ఇన్ చేయండి",
            "kn" to "ಸೈನ್ ಇನ್ ಮಾಡಿ",
            "ml" to "സൈൻ ഇൻ ചെയ്യുക",
            "bn" to "সাইন ইন করুন"
        ),
        "Email or Phone" to mapOf(
            "hi" to "ईमेल या फोन",
            "ta" to "மின்னஞ்சல் அல்லது தொலைபேசி",
            "te" to "ఇమెయిల్ లేదా ఫోన్",
            "kn" to "ಇಮೇಲ್ ಅಥವಾ ಫೋನ್",
            "ml" to "ഇമെയിൽ അല്ലെങ്കിൽ ഫോൺ",
            "bn" to "ইমেইল বা ফোন"
        ),
        "Password" to mapOf(
            "hi" to "पासवर्ड",
            "ta" to "கடவுச்சொல்",
            "te" to "పాస్వర్డ్",
            "kn" to "ಪಾಸ್ವರ್ಡ್",
            "ml" to "പാസ്‌വേഡ്",
            "bn" to "পাসওয়ার্ড"
        ),
        "Change role" to mapOf(
            "hi" to "भूमিকা बदलें",
            "ta" to "பங்கை மாற்று",
            "te" to "పాత్రను మార్చండి",
            "kn" to "ಪಾತ್ರವನ್ನು ಬದಲಾಯಿಸಿ",
            "ml" to "റോൾ മാറ്റുക",
            "bn" to "ভূমিকা পরিবর্তন করুন"
        ),
        "Emergency Medical Triage System" to mapOf(
            "hi" to "आपातकालीन चिकित्सा ट्राइएज प्रणाली",
            "ta" to "அவசர மருத்துவ ட்ரைஜ் அமைப்பு",
            "te" to "అత్యవసర వైద్య ట్రయాజ్ సిస్టమ్",
            "kn" to "ತುರ್ತು ವೈದ್ಯಕೀಯ ಟ್ರಯಾಜ್ ವ್ಯವಸ್ಥೆ",
            "ml" to "അടിയന്തര മെഡിക്കൽ ട്രയേജ് സിസ്റ്റം",
            "bn" to "জরুরী মেডিকেল ট্রায়াজ সিস্টেম"
        ),
        "Dashboard" to mapOf(
            "hi" to "डैशबोर्ड",
            "ta" to "டாஷ்போர்டு",
            "te" to "డాష్‌బోర్డ్",
            "kn" to "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
            "ml" to "ഡാഷ്‌ബോർഡ്",
            "bn" to "ড্যাশবোর্ড"
        ),
        "Triage" to mapOf(
            "hi" to "ट्राइएज",
            "ta" to "ட்ரைஜ்",
            "te" to "ట్రయాజ్",
            "kn" to "ಟ್ರಯಾಜ್",
            "ml" to "ട്രയേജ്",
            "bn" to "ট্রায়াজ"
        ),
        "Hospitals" to mapOf(
            "hi" to "अस्पताल",
            "ta" to "மருத்துவமனைகள்",
            "te" to "ఆసుపత్రులు",
            "kn" to "ಆಸ್ಪತ್ರೆಗಳು",
            "ml" to "ആശുപത്രികൾ",
            "bn" to "হাসপাতাল"
        ),
        "More" to mapOf(
            "hi" to "अधिक",
            "ta" to "மேலும்",
            "te" to "మరింత",
            "kn" to "ಇನ್ನಷ್ಟು",
            "ml" to "കൂടുതൽ",
            "bn" to "আরও"
        ),
        "Patient Information" to mapOf(
            "hi" to "रोगी की जानकारी",
            "ta" to "நோயாளி தகவல்",
            "te" to "రోగి సమాచారం",
            "kn" to "ರೋಗಿಯ ಮಾಹಿತಿ",
            "ml" to "രോഗിയുടെ വിവരങ്ങൾ",
            "bn" to "রোগীর তথ্য"
        ),
        "Age" to mapOf(
            "hi" to "आयु",
            "ta" to "வயது",
            "te" to "వయస్సు",
            "kn" to "ವಯಸ್ಸು",
            "ml" to "പ്രായം",
            "bn" to "বয়স"
        ),
        "Gender" to mapOf(
            "hi" to "लिंग",
            "ta" to "பாலினம்",
            "te" to "లింగం",
            "kn" to "ಲಿಂಗ",
            "ml" to "ലിംഗഭേദം",
            "bn" to "লিঙ্গ"
        ),
        "Symptoms & History" to mapOf(
            "hi" to "लक्षण और इतिहास",
            "ta" to "அறிகுறிகள் மற்றும் வரலாறு",
            "te" to "లక్షణాలు మరియు చరిత్ర",
            "kn" to "ಲಕ್ಷಣಗಳು ಮತ್ತು ಇತಿಹಾಸ",
            "ml" to "രോഗലക്ഷണങ്ങളും ചരിത്രവും",
            "bn" to "উপসর্গ এবং ইতিহাস"
        ),
        "Vitals" to mapOf(
            "hi" to "वाइटल्स",
            "ta" to "வைட்டல்ஸ்",
            "te" to "వైటల్స్",
            "kn" to "ವೈಟಲ್ಸ್",
            "ml" to "വൈറ്റൽസ്",
            "bn" to "ভাইটাল"
        ),
        "Medical history (optional)" to mapOf(
            "hi" to "चिकित्सा इतिहास (वैकल्पिक)",
            "ta" to "மருத்துவ வரலாறு (விருப்பமானது)",
            "te" to "వైద్య చరిత్ర (ఐచ్ఛికం)",
            "kn" to "ವೈದ್ಯಕೀಯ ಇತಿಹಾಸ (ಐಚ್ಛಿಕ)",
            "ml" to "മെഡിക്കൽ ചരിത്രം (ഓപ്ഷണൽ)",
            "bn" to "চিকিৎসা ইতিহাস (ঐচ্ছিক)"
        ),
        "Allergies (optional)" to mapOf(
            "hi" to "एलर्जी (वैकल्पिक)",
            "ta" to "ஒவ்வாமை (விருப்பமானது)",
            "te" to "అలెర్జీలు (ఐచ్ఛికం)",
            "kn" to "ಅಲರ್ಜಿಗಳು (ಐಚ್ಛಿಕ)",
            "ml" to "അലർജികൾ (ഓപ്ഷണൽ)",
            "bn" to "অ্যালার্জি (ঐচ্ছিক)"
        ),
        "Start" to mapOf(
            "hi" to "शुरू करें",
            "ta" to "தொடங்கு",
            "te" to "ప్రారంభించండి",
            "kn" to "ಪ್ರಾರಂಭಿಸಿ",
            "ml" to "തുടങ്ങുക",
            "bn" to "শুরু করুন"
        ),
        "Next" to mapOf(
            "hi" to "अगला",
            "ta" to "அடுத்து",
            "te" to "తరువాత",
            "kn" to "ಮುಂದೆ",
            "ml" to "അടുത്തത്",
            "bn" to "পরবর্তী"
        ),
        "Loading…" to mapOf(
            "hi" to "लोड हो रहा है…",
            "ta" to "ஏற்றுகிறது…",
            "te" to "లోడ్ అవుతోంది…",
            "kn" to "ಲೋಡ್ ಆಗುತ್ತಿದೆ…",
            "ml" to "ലോഡ് ചെയ്യുന്നു…",
            "bn" to "লোড হচ্ছে…"
        ),
        "Step" to mapOf(
            "hi" to "चरण",
            "ta" to "படி",
            "te" to "దశ",
            "kn" to "ಹಂತ",
            "ml" to "ഘട്ടം",
            "bn" to "ধাপ"
        ),
        "of" to mapOf(
            "hi" to "का",
            "ta" to "இல்",
            "te" to "లో",
            "kn" to "ರಲ್ಲಿ",
            "ml" to "ൽ",
            "bn" to "এর"
        ),
        "Symptoms" to mapOf(
            "hi" to "लक्षण",
            "ta" to "அறிகுறிகள்",
            "te" to "లక్షణాలు",
            "kn" to "ಲಕ್ಷಣಗಳು",
            "ml" to "രോഗലക്ഷണങ്ങൾ",
            "bn" to "উপসর্গ"
        ),
        "Describe symptoms *" to mapOf(
            "hi" to "लक्षणों का वर्णन करें *",
            "ta" to "அறிகுறிகளை விவரிக்கவும் *",
            "te" to "లక్షణాలను వివరించండి *",
            "kn" to "ಲಕ್ಷಣಗಳನ್ನು ವಿವರಿಸಿ *",
            "ml" to "രോഗലക്ഷണങ്ങൾ വിവരിക്കുക *",
            "bn" to "উপসর্গ বর্ণনা করুন *"
        ),
        "Duration (minutes)" to mapOf(
            "hi" to "अवधि (मिनट)",
            "ta" to "கால அளவு (நிமிடங்கள்)",
            "te" to "వ్యవధి (నిమిషాలు)",
            "kn" to "ಅವಧಿ (ನಿಮಿಷಗಳು)",
            "ml" to "ദൈർഘ്യം (മിനിറ്റ്)",
            "bn" to "সময়কাল (মিনিট)"
        ),
        "Patient-reported severity" to mapOf(
            "hi" to "रोगी द्वारा बताई गई गंभीरता",
            "ta" to "நோயாளி தெரிவித்த தீவிரம்",
            "te" to "రోగి నివేదించిన తీవ్రత",
            "kn" to "ರೋಗಿ ವರದಿ ಮಾಡಿದ ತೀವ್ರತೆ",
            "ml" to "രോഗി റിപ്പോർട്ട് ചെയ്ത തീവ്രത",
            "bn" to "রোগীর রিপোর্ট করা তীব্রতা"
        ),
        "Heart rate (bpm)" to mapOf(
            "hi" to "हृदय गति (bpm)",
            "ta" to "இதயத் துடிப்பு (bpm)",
            "te" to "హృదయ స్పందన రేటు (bpm)",
            "kn" to "ಹೃದಯ ಬಡಿತ (bpm)",
            "ml" to "ഹൃദയമിടിപ്പ് (bpm)",
            "bn" to "হৃদস্পন্দন (bpm)"
        ),
        "BP systolic" to mapOf(
            "hi" to "बीपी सिस्टोलिक",
            "ta" to "பிபி சிஸ்டாலிக்",
            "te" to "బిపి సిస్టోలిక్",
            "kn" to "ಬಿಪಿ ಸಿಸ್ಟೊಲಿಕ್",
            "ml" to "ബിപി സിസ്റ്റോളിക്",
            "bn" to "বিপি সিস্টোলিক"
        ),
        "BP diastolic" to mapOf(
            "hi" to "बीपी डायस्टोलिक",
            "ta" to "பிபி டயஸ்டாலிக்",
            "te" to "బిపి డయాస్టోలిక్",
            "kn" to "ಬಿಪಿ ಡಯಾಸ್ಟೊಲಿಕ್",
            "ml" to "ബിപി ഡയസ്റ്റോളിക്",
            "bn" to "বিপি ডায়াস্টোলিক"
        ),
        "Temperature (°C)" to mapOf(
            "hi" to "तापमान (°C)",
            "ta" to "வெப்பநிலை (°C)",
            "te" to "ఉష్ణోగ్రత (°C)",
            "kn" to "ತಾಪಮಾನ (°C)",
            "ml" to "താപനില (°C)",
            "bn" to "তাপমাত্রা (°C)"
        ),
        "SpO2 (%)" to mapOf(
            "hi" to "SpO2 (%)",
            "ta" to "SpO2 (%)",
            "te" to "SpO2 (%)",
            "kn" to "SpO2 (%)",
            "ml" to "SpO2 (%)",
            "bn" to "SpO2 (%)"
        ),
        "Respiratory rate" to mapOf(
            "hi" to "श्वसन दर",
            "ta" to "சுவாச விகிதம்",
            "te" to "శ్వసన రేటు",
            "kn" to "ಶ್ವಾಸಕೋಶದ ದರ",
            "ml" to "ശ്വസന നിരക്ക്",
            "bn" to "শ্বাসপ্রশ্বাস হার"
        ),
        "Consciousness (AVPU)" to mapOf(
            "hi" to "चेतना (AVPU)",
            "ta" to "நினைவுத்திறன் (AVPU)",
            "te" to "స్పృహ (AVPU)",
            "kn" to "ಪ್ರಜ್ಞೆ (AVPU)",
            "ml" to "ബോധം (AVPU)",
            "bn" to "চেতনা (AVPU)"
        ),
        "Assess" to mapOf(
            "hi" to "आकलन करें",
            "ta" to "மதிப்பிடு",
            "te" to "అంచనా వేయండి",
            "kn" to "ಮೌಲ್ಯಮಾಪನ ಮಾಡಿ",
            "ml" to "വിലയിരുത്തുക",
            "bn" to "মূল্যায়ন করুন"
        ),
        "Assessing…" to mapOf(
            "hi" to "आकलन किया जा रहा है…",
            "ta" to "மதிப்பிடுகிறது…",
            "te" to "అంచనా వేస్తోంది…",
            "kn" to "ಮೌಲ್ಯಮಾಪನ ಮಾಡಲಾಗುತ್ತಿದೆ…",
            "ml" to "വിലയിരുത്തുന്നു…",
            "bn" to "মূল্যায়ন করা হচ্ছে…"
        ),
        "Switch to light theme" to mapOf(
            "hi" to "लाइट थीम पर स्विच करें",
            "ta" to "ஒளி தீமிற்கு மாற்றவும்",
            "te" to "లైట్ థీమ్‌కు మారండి",
            "kn" to "ಲೈಟ್ ಥೀಮ್‌ಗೆ ಬದಲಾಯಿಸಿ",
            "ml" to "ലൈറ്റ് തീമിലേക്ക് മാറുക",
            "bn" to "লাইট থিমে স্যুইচ করুন"
        ),
        "Switch to dark theme" to mapOf(
            "hi" to "डार्क थीम पर स्विच करें",
            "ta" to "இருண்ட தீமிற்கு மாற்றவும்",
            "te" to "డార్క్ థీమ్‌కు మారండి",
            "kn" to "ಡಾರ್ಕ್ ಥೀಮ್‌ಗೆ ಬದಲಾಯಿಸಿ",
            "ml" to "ഡാർക്ക് തീമിലേക്ക് മാറുക",
            "bn" to "ডার্ক থিমে স্যুইচ করুন"
        )
    )
}
