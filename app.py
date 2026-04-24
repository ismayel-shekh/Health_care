import streamlit as st
from dotenv import load_dotenv
import os
import textwrap
import google.generativeai as genai
import requests
from urllib.parse import urlparse, parse_qs

# Load environment variables
load_dotenv()

# Custom CSS
css = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

.stApp {
  background-color: #ac998d;
  background-image:
    radial-gradient(circle at 14% 15%, rgba(255, 205, 96, 0.28) 0 120px, transparent 130px),
    radial-gradient(circle at 88% 8%, rgba(255, 255, 255, 0.38) 0 170px, transparent 180px),
    radial-gradient(circle at 84% 86%, rgba(9, 85, 58, 0.18) 0 220px, transparent 230px),
    linear-gradient(120deg, #ab988c 0%, #c6b5a8 50%, #aa978a 100%);
  min-height: 100vh;
  font-family: 'DM Sans', sans-serif;
  color: #332720;
}

.main .block-container {
  background: linear-gradient(180deg, #f9f5ef 0%, #fffdf9 72%, #f8f2e8 100%);
  border-radius: 22px;
  padding: 2.7rem 1.7rem 2rem;
  box-shadow: 0 20px 46px rgba(45, 29, 19, 0.26);
  border: 1px solid rgba(82, 57, 36, 0.15);
  position: relative;
  overflow: hidden;
  max-width: 1200px;
}

.main .block-container::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: min(40%, 430px);
  height: 100%;
  background: linear-gradient(180deg, #034a33 0%, #0c6448 45%, #0a5940 100%);
  clip-path: polygon(30% 0, 100% 0, 100% 100%, 0 100%);
  opacity: 0.18;
  pointer-events: none;
}

.main .block-container::after {
  content: '';
  position: absolute;
  left: -90px;
  bottom: -110px;
  width: 340px;
  height: 340px;
  border-radius: 50%;
  background: radial-gradient(circle at center, rgba(255, 174, 74, 0.3) 0, rgba(255, 174, 74, 0.03) 72%);
  pointer-events: none;
}

/* Decorative top strip to emulate reference navbar area */
.main .block-container > div:first-child::before {
  content: '';
  position: absolute;
  top: 0.9rem;
  left: 1.7rem;
  right: 1.7rem;
  height: 48px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid rgba(99, 72, 50, 0.15);
  box-shadow: 0 3px 10px rgba(48, 36, 26, 0.08);
  z-index: 0;
  pointer-events: none;
}

.st-emotion-cache-1v0mbdj {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.07);
  padding: 2rem;
}
.hero-title {
  font-family: 'Fraunces', serif;
  font-size: clamp(2.2rem, 5vw, 4rem);
  font-weight: 700;
  line-height: 1.03;
  letter-spacing: -0.02em;
  color: #4f2f20;
  margin-bottom: 0.8rem;
  max-width: 12ch;
  position: relative;
  z-index: 1;
  margin-top: 1.35rem;
}
.hero-title::before {
  content: 'MENTAL HEALTH AI SUPPORT';
  display: inline-block;
  margin-bottom: 0.9rem;
  padding: 0.28rem 0.75rem;
  border-radius: 999px;
  border: 1px solid rgba(85, 61, 43, 0.28);
  background: #fffaf1;
  color: #4e4139;
  font-family: 'DM Sans', sans-serif;
  font-weight: 700;
  font-size: 0.67rem;
  letter-spacing: 0.08em;
}
.hero-sub {
  font-size: 1.05rem;
  color: #534640;
  max-width: 55ch;
  line-height: 1.55;
  margin-bottom: 2rem;
  position: relative;
  z-index: 1;
}
.stForm {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(102, 74, 52, 0.18);
  border-radius: 16px;
  padding: 1rem 1rem 0.3rem;
  backdrop-filter: blur(1.5px);
}
.result-card {
  background: linear-gradient(135deg, #fff7e8 0%, #fffefb 100%);
  border-radius: 16px;
  border: 1px solid rgba(91, 62, 39, 0.2);
  padding: 1.5rem;
  margin-top: 1.5rem;
  box-shadow: 0 8px 20px rgba(62, 42, 27, 0.12);
}
.hospital-card {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}
.doctor-card {
  background: linear-gradient(135deg, #ffffff 0%, #f0fef9 100%);
  border: 1px solid #d0e8e4;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.doctor-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.2);
}
.doctor-image {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  margin: 0 auto 1rem;
  object-fit: cover;
  border: 3px solid #10b981;
}
.doctor-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.3rem;
}
.doctor-specialization {
  font-size: 0.9rem;
  color: #10b981;
  font-weight: 600;
  margin-bottom: 0.8rem;
}
.doctor-description {
  font-size: 0.85rem;
  color: #6b7280;
  margin-bottom: 0.8rem;
  line-height: 1.4;
}
.doctor-hospital {
  font-size: 0.85rem;
  color: #374151;
  font-weight: 500;
  margin-bottom: 1rem;
  padding-top: 0.8rem;
  border-top: 1px solid #e5e7eb;
}
.doctor-buttons {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}
.section-title {
  font-family: 'Fraunces', serif;
  font-size: clamp(1.6rem, 3.5vw, 2.3rem);
  font-weight: 700;
  color: #2d241f;
  margin-top: 2rem;
  margin-bottom: 1.5rem;
  max-width: 22ch;
}
.credential-card {
  background: linear-gradient(180deg, #fffaf0 0%, #fff 100%);
  border: 1px solid rgba(70, 50, 33, 0.22);
  border-radius: 18px;
  padding: 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 12px 28px rgba(40, 28, 19, 0.16);
  position: relative;
  overflow: hidden;
}
.credential-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 9px;
  height: 100%;
  background: linear-gradient(180deg, #ffad52 0%, #ec8a2d 100%);
}
.credential-header {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
  align-items: flex-start;
  flex-wrap: wrap;
}
.credential-image {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  border: 4px solid #6f4e3b;
  object-fit: cover;
  flex-shrink: 0;
  box-shadow: 0 7px 16px rgba(78, 52, 33, 0.26);
}
.credential-info {
  flex: 1;
  min-width: 0;
}
.credential-name {
  font-family: 'Fraunces', serif;
  font-size: 1.7rem;
  font-weight: 700;
  color: #2f231c;
  margin-bottom: 0.3rem;
  word-break: break-word;
}
.credential-spec {
  font-size: 1rem;
  color: #0d6f50;
  font-weight: 600;
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.credential-badge {
  background: linear-gradient(135deg, #0b5f44 0%, #0e7152 100%);
  color: white;
  padding: 0.48rem 1rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  display: inline-block;
  margin-bottom: 1rem;
}
.credential-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  background: rgba(255, 173, 82, 0.09);
  padding: 1.5rem;
  border-radius: 12px;
}
.detail-item {
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.8rem;
}
.detail-label {
  font-size: 0.75rem;
  color: #695d56;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.detail-value {
  font-size: 1rem;
  color: #29211c;
  font-weight: 600;
  margin-top: 0.3rem;
  font-family: 'Courier New', monospace;
  overflow-wrap: anywhere;
}
.hospital-section {
  background: linear-gradient(145deg, #024d35 0%, #076447 100%);
  color: white;
  padding: 1.3rem;
  border-radius: 14px;
  margin-top: 1.5rem;
}
.hospital-name {
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: 1rem;
}
.hospital-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  font-size: 0.9rem;
  line-height: 1.6;
}
.hospital-detail {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  min-width: 0;
}
.hospital-detail-icon {
  color: #ffd166;
  font-weight: bold;
  min-width: 20px;
}
.hospital-detail span:last-child {
  overflow-wrap: anywhere;
}
.contact-button {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  margin-top: 1rem;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}
.contact-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(6, 182, 212, 0.4);
}

.emergency {
  color: #e53e3e;
  font-weight: bold;
}
.urgent {
  color: #d69e2e;
  font-weight: bold;
}
.normal {
  color: #38a169;
  font-weight: bold;
}
.disclaimer {
  font-size: 0.95rem;
  color: #5e4f46;
  margin-top: 2rem;
  text-align: center;
}
.stButton>button {
  border-radius: 999px;
  font-weight: 600;
  padding: 0.62rem 1.25rem;
  border: 0;
  color: #fff8ef;
  background: linear-gradient(145deg, #1c1612 0%, #30251f 100%);
  box-shadow: 0 7px 16px rgba(26, 20, 15, 0.25);
  transition: transform 0.2s ease, background 0.2s ease;
}
.stButton>button:hover {
  transform: translateY(-1px);
  background: linear-gradient(145deg, #2a211b 0%, #3a2e28 100%);
}
.stButton>button:disabled {
  opacity: 0.5;
}

[data-testid="stMarkdownContainer"] p {
  line-height: 1.55;
}

textarea,
input,
select,
.stTextArea textarea,
.stTextInput input,
.stSelectbox div[data-baseweb="select"] > div {
  border-radius: 14px !important;
  border: 1px solid rgba(97, 67, 44, 0.25) !important;
  background: #fffdf9 !important;
}

@media (max-width: 1200px) {
  .main .block-container::before {
    width: min(42%, 280px);
    opacity: 0.1;
  }
  .main .block-container > div:first-child::before {
    left: 1.2rem;
    right: 1.2rem;
  }
  .credential-card {
    padding: 1.25rem;
  }
  .credential-header {
    gap: 1rem;
  }
  .credential-image {
    width: 110px;
    height: 110px;
  }
  .credential-name {
    font-size: 1.25rem;
  }
  .credential-details,
  .hospital-details {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .main .block-container {
    border-radius: 18px;
    padding: 1.1rem 0.9rem 1.4rem;
  }
  .main .block-container > div:first-child::before,
  .main .block-container::before,
  .main .block-container::after {
    display: none;
  }
  .hero-title {
    margin-top: 0;
  }
  .credential-card {
    padding: 1rem;
  }
  .credential-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  .credential-image {
    width: 96px;
    height: 96px;
  }
  .credential-badge {
    font-size: 0.8rem;
  }
}
"""
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Helper function to extract location from URL or address
def parse_location_input(location_input):
    """Extract location from Google Maps URL or return plain address."""
    if not location_input:
        return None
    
    # Check if it's a Google Maps URL
    if "google.com/maps" in location_input.lower():
        try:
            # Try to extract place name from URL
            if "/place/" in location_input:
                place_name = location_input.split("/place/")[1].split("/")[0]
                place_name = place_name.replace("+", " ").split(",")[0]
                return place_name
        except:
            pass
        return "Kedah"  # Default extraction fallback
    
    # Return as-is if it's a plain address
    return location_input

# Functions
def get_gemini_response(symptoms, urgency, location=None):
    prompt = f"""
    Analyze the following patient symptoms and provide structured output:
    - Emergency level (Emergency / Urgent / Normal)
    - Should the patient call an ambulance? (Yes/No + reason)
    - Possible condition (general, not medical diagnosis)
    - Immediate first aid suggestions
    - Safety advice

    Symptoms: {symptoms}
    Urgency: {urgency}
    Location: {location if location else 'Not provided'}
    """
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3-flash-preview")
    response = model.generate_content(prompt)
    return response.text

def get_doctors_data():
    """Returns a list of 20+ mock doctor objects with detailed information."""
    doctors = [
        {
            "doctor_name": "Dr. Rajesh Kumar",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Rajesh_Kumar",
            "specialization": "Cardiologist",
            "description": "Expert in heart diseases and cardiovascular care with 12+ years experience.",
            "hospital_name": "Kedah Heart Care Hospital",
            "location": "Alor Setar, Kedah",
            "license_no": "MED-2012-4521",
            "issue_date": "03/15/2012",
            "expiration_date": "03/15/2026",
            "phone": "011-1234-5678",
            "email": "rajesh.kumar@heartcare.com.my"
        },
        {
            "doctor_name": "Dr. Priya Sharma",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Priya_Sharma",
            "specialization": "General Physician",
            "description": "Comprehensive care and diagnosis for various health conditions.",
            "hospital_name": "Premier Medical Center",
            "location": "Kuala Lumpur",
            "license_no": "MED-2015-7832",
            "issue_date": "06/20/2015",
            "expiration_date": "06/20/2026",
            "phone": "012-2345-6789",
            "email": "priya.sharma@premiermed.com.my"
        },
        {
            "doctor_name": "Dr. Ahmad Hassan",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Ahmad_Hassan",
            "specialization": "Pulmonologist",
            "description": "Specialized in respiratory and lung diseases.",
            "hospital_name": "Respire Lung Clinic",
            "location": "Kuala Lumpur",
            "license_no": "MED-2013-9254",
            "issue_date": "09/10/2013",
            "expiration_date": "09/10/2025",
            "phone": "013-3456-7890",
            "email": "ahmad.hassan@respire.com.my"
        },
        {
            "doctor_name": "Dr. Siti Nur Azizah",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Siti_Nur_Azizah",
            "specialization": "Neurologist",
            "description": "Expert in neurological disorders and brain health.",
            "hospital_name": "Neuro Excellence Center",
            "location": "Selangor",
            "license_no": "MED-2014-5673",
            "issue_date": "05/22/2014",
            "expiration_date": "05/22/2026",
            "phone": "014-4567-8901",
            "email": "siti.azizah@neuro.com.my"
        },
        {
            "doctor_name": "Dr. Mohammad Ali",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Mohammad_Ali",
            "specialization": "Orthopedist",
            "description": "Specialist in bone, joint, and muscle disorders.",
            "hospital_name": "Bone & Joint Institute",
            "location": "Penang",
            "license_no": "MED-2011-3891",
            "issue_date": "11/08/2011",
            "expiration_date": "11/08/2025",
            "phone": "016-5678-9012",
            "email": "mohammad.ali@ortho.com.my"
        },
        {
            "doctor_name": "Dr. Sophia Lee",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Sophia_Lee",
            "specialization": "Gastroenterologist",
            "description": "Expert in digestive system and gastrointestinal health.",
            "hospital_name": "Digestive Care Hospital",
            "location": "Kuala Lumpur",
            "license_no": "MED-2016-2145",
            "issue_date": "02/14/2016",
            "expiration_date": "02/14/2026",
            "phone": "017-6789-0123",
            "email": "sophia.lee@digcare.com.my"
        },
        {
            "doctor_name": "Dr. Arun Patel",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Arun_Patel",
            "specialization": "ENT Specialist",
            "description": "Specialized in ear, nose, and throat disorders.",
            "hospital_name": "ENT Excellence Clinic",
            "location": "Selangor",
            "license_no": "MED-2012-7654",
            "issue_date": "07/19/2012",
            "expiration_date": "07/19/2025",
            "phone": "018-7890-1234",
            "email": "arun.patel@ent.com.my"
        },
        {
            "doctor_name": "Dr. Maria Santos",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Maria_Santos",
            "specialization": "General Physician",
            "description": "Compassionate doctor with focus on patient wellness.",
            "hospital_name": "Wellness Medical Center",
            "location": "Klang",
            "license_no": "MED-2017-1234",
            "issue_date": "01/09/2017",
            "expiration_date": "01/09/2027",
            "phone": "019-8901-2345",
            "email": "maria.santos@wellness.com.my"
        },
        {
            "doctor_name": "Dr. Chen Wei",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Chen_Wei",
            "specialization": "Cardiologist",
            "description": "Advanced cardiac imaging and intervention specialist.",
            "hospital_name": "Cardiac Care Excellence",
            "location": "Petaling Jaya",
            "license_no": "MED-2010-5432",
            "issue_date": "04/11/2010",
            "expiration_date": "04/11/2025",
            "phone": "010-9012-3456",
            "email": "chen.wei@cardiac.com.my"
        },
        {
            "doctor_name": "Dr. Fatima Al-Zahra",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Fatima_Al_Zahra",
            "specialization": "Pulmonologist",
            "description": "Experienced in asthma, COPD, and critical respiratory care.",
            "hospital_name": "Respire Lung Clinic",
            "location": "Shah Alam",
            "license_no": "MED-2014-8765",
            "issue_date": "08/25/2014",
            "expiration_date": "08/25/2026",
            "phone": "011-0123-4567",
            "email": "fatima.alzahra@respire.com.my"
        },
        {
            "doctor_name": "Dr. David Thompson",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_David_Thompson",
            "specialization": "Neurologist",
            "description": "Specialist in stroke, epilepsy, and neurological emergencies.",
            "hospital_name": "Neuro Excellence Center",
            "location": "Kuala Lumpur",
            "license_no": "MED-2009-4321",
            "issue_date": "10/02/2009",
            "expiration_date": "10/02/2024",
            "phone": "012-1234-5678",
            "email": "david.thompson@neuro.com.my"
        },
        {
            "doctor_name": "Dr. Anjali Gupta",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Anjali_Gupta",
            "specialization": "Orthopedist",
            "description": "Expert in sports medicine and joint rehabilitation.",
            "hospital_name": "Sports Medicine Clinic",
            "location": "Subang Jaya",
            "license_no": "MED-2015-9876",
            "issue_date": "12/03/2015",
            "expiration_date": "12/03/2025",
            "phone": "013-2345-6789",
            "email": "anjali.gupta@sports.com.my"
        },
        {
            "doctor_name": "Dr. James Wilson",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_James_Wilson",
            "specialization": "Gastroenterologist",
            "description": "Specialist in endoscopy and GI procedures.",
            "hospital_name": "GI Health Center",
            "location": "Bukit Jalil",
            "license_no": "MED-2013-2468",
            "issue_date": "05/17/2013",
            "expiration_date": "05/17/2026",
            "phone": "014-3456-7890",
            "email": "james.wilson@gihealth.com.my"
        },
        {
            "doctor_name": "Dr. Nina Kapoor",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Nina_Kapoor",
            "specialization": "ENT Specialist",
            "description": "Expert in sinus, hearing, and voice disorders.",
            "hospital_name": "ENT Excellence Clinic",
            "location": "Kuala Lumpur",
            "license_no": "MED-2016-1357",
            "issue_date": "09/29/2016",
            "expiration_date": "09/29/2026",
            "phone": "015-4567-8901",
            "email": "nina.kapoor@ent.com.my"
        },
        {
            "doctor_name": "Dr. Hassan Ibrahim",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Hassan_Ibrahim",
            "specialization": "General Physician",
            "description": "24/7 emergency medicine and acute care expert.",
            "hospital_name": "Emergency Care Center",
            "location": "Ampang",
            "license_no": "MED-2011-8642",
            "issue_date": "06/12/2011",
            "expiration_date": "06/12/2025",
            "phone": "016-5678-9012",
            "email": "hassan.ibrahim@emcare.com.my"
        },
        {
            "doctor_name": "Dr. Lisa Wang",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Lisa_Wang",
            "specialization": "Cardiologist",
            "description": "Preventive cardiology and heart disease management.",
            "hospital_name": "Preventive Heart Clinic",
            "location": "Bangsar",
            "license_no": "MED-2014-7531",
            "issue_date": "03/08/2014",
            "expiration_date": "03/08/2026",
            "phone": "017-6789-0123",
            "email": "lisa.wang@cardiac.com.my"
        },
        {
            "doctor_name": "Dr. Ravi Shankar",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Ravi_Shankar",
            "specialization": "Pulmonologist",
            "description": "Critical care and intensive respiratory support.",
            "hospital_name": "Critical Care Hospital",
            "location": "Cheras",
            "license_no": "MED-2012-9517",
            "issue_date": "11/20/2012",
            "expiration_date": "11/20/2025",
            "phone": "018-7890-1234",
            "email": "ravi.shankar@critical.com.my"
        },
        {
            "doctor_name": "Dr. Amelia Brown",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Amelia_Brown",
            "specialization": "Neurologist",
            "description": "Pediatric neurology and developmental disorders specialist.",
            "hospital_name": "Child Neurology Center",
            "location": "Sentosa",
            "license_no": "MED-2016-3579",
            "issue_date": "07/14/2016",
            "expiration_date": "07/14/2026",
            "phone": "019-8901-2345",
            "email": "amelia.brown@neuro.com.my"
        },
        {
            "doctor_name": "Dr. Marco Rossi",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Marco_Rossi",
            "specialization": "Orthopedist",
            "description": "Orthopedic surgery and trauma care specialist.",
            "hospital_name": "Trauma & Orthopedic Institute",
            "location": "Melawati",
            "license_no": "MED-2010-7642",
            "issue_date": "02/28/2010",
            "expiration_date": "02/28/2025",
            "phone": "010-9012-3456",
            "email": "marco.rossi@trauma.com.my"
        },
        {
            "doctor_name": "Dr. Zainab Ahmed",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Zainab_Ahmed",
            "specialization": "Gastroenterologist",
            "description": "Liver disease and hepatology specialist.",
            "hospital_name": "Liver Care Center",
            "location": "Damansara",
            "license_no": "MED-2015-2486",
            "issue_date": "09/05/2015",
            "expiration_date": "09/05/2025",
            "phone": "011-0123-4567",
            "email": "zainab.ahmed@liver.com.my"
        },
        {
            "doctor_name": "Dr. Victor Chen",
            "image_url": "https://api.dicebear.com/9.x/avataaars/svg?seed=Dr_Victor_Chen",
            "specialization": "ENT Specialist",
            "description": "Otologic surgery and hearing rehabilitation expert.",
            "hospital_name": "Hearing Care Clinic",
            "location": "Cyberjaya",
            "license_no": "MED-2017-5739",
            "issue_date": "04/19/2017",
            "expiration_date": "04/19/2027",
            "phone": "012-1234-5678",
            "email": "victor.chen@hearing.com.my"
        }
    ]
    return doctors

def filter_doctors_by_symptoms(symptoms, all_doctors):
    """Filter doctors based on detected symptom keywords."""
    symptoms_lower = symptoms.lower()
    
    specialization_keywords = {
        "Cardiologist": ["chest pain", "heart", "cardiac", "palpitation", "arrhythmia", "breathlessness", "pressure"],
        "Pulmonologist": ["cough", "breathing", "shortness", "breath", "lungs", "respiratory", "wheeze", "asthma"],
        "General Physician": ["fever", "cold", "flu", "ache", "fatigue", "general", "illness", "sick"],
        "Neurologist": ["headache", "migraine", "dizziness", "vertigo", "seizure", "brain", "memory", "numbness"],
        "Orthopedist": ["bone", "joint", "fracture", "sprain", "muscle", "pain", "back", "knee", "leg", "arm"],
        "Gastroenterologist": ["stomach", "nausea", "vomiting", "diarrhea", "digestion", "stomach pain", "abdomen"],
        "ENT Specialist": ["throat", "ear", "nose", "sore", "congestion", "sinus", "hearing"]
    }
    
    matched_specializations = set()
    for spec, keywords in specialization_keywords.items():
        if any(keyword in symptoms_lower for keyword in keywords):
            matched_specializations.add(spec)
    
    # Filter doctors by matched specializations
    if matched_specializations:
        filtered = [doc for doc in all_doctors if doc["specialization"] in matched_specializations]
        return filtered if filtered else all_doctors[:5]
    
    # Return top 5 if no matches
    return all_doctors[:5]

def display_doctor_cards(doctors_to_display):
    """Display professional doctor credential cards in a responsive 2-column grid."""
    for i in range(0, len(doctors_to_display), 2):
        row_doctors = doctors_to_display[i:i+2]
        cols = st.columns(2)
        for col, doctor in zip(cols, row_doctors):
            credential_html = f"""
<div class="credential-card">
    <div class="credential-header">
        <img src="{doctor['image_url']}" alt="{doctor['doctor_name']}" class="credential-image">
        <div class="credential-info">
            <div class="credential-name">{doctor['doctor_name']}</div>
            <div class="credential-spec">{doctor['specialization']}</div>
            <div class="credential-badge">✓ Licensed & Verified</div>
        </div>
    </div>
    <div class="credential-details">
        <div class="detail-item">
            <div class="detail-label">License #</div>
            <div class="detail-value">{doctor['license_no']}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Issue Date</div>
            <div class="detail-value">{doctor['issue_date']}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Expiration Date</div>
            <div class="detail-value">{doctor['expiration_date']}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Phone</div>
            <div class="detail-value">{doctor['phone']}</div>
        </div>
    </div>
    <div class="hospital-section">
        <div class="hospital-name">🏥 {doctor['hospital_name']}</div>
        <div class="hospital-details">
            <div class="hospital-detail">
                <span class="hospital-detail-icon">📍</span>
                <span>{doctor['location']}</span>
            </div>
            <div class="hospital-detail">
                <span class="hospital-detail-icon">✉️</span>
                <span>{doctor['email']}</span>
            </div>
            <div class="hospital-detail">
                <span class="hospital-detail-icon">📞</span>
                <span>{doctor['phone']}</span>
            </div>
        </div>
    </div>
</div>
"""
            rendered_html = textwrap.dedent(credential_html).strip()
            col.markdown(rendered_html, unsafe_allow_html=True)

# --- UI ---
st.markdown('<div class="hero-title">Emergency AI Health Support</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Describe your symptoms and get instant AI-powered emergency guidance.</div>', unsafe_allow_html=True)

with st.form("symptom_form"):
    symptoms = st.text_area("Describe your symptoms", max_chars=500, height=120)
    urgency = st.selectbox("Urgency level", ["Low", "Medium", "High"])
    location = st.text_input("Your location (city, postcode, or full address)", 
                             placeholder="e.g., Kedah, Malaysia or Kuala Lumpur")
    st.caption("💡 Tip: Enter a plain address (not a Google Maps URL)")
    submitted = st.form_submit_button("Analyze Symptoms")

ai_output = ""
emergency_level = ""
if submitted and symptoms.strip():
    # Parse and store location
    parsed_location = parse_location_input(location)
    if not parsed_location:
        st.error("❌ Please enter a valid location")
    else:
        # Store form data in session state
        st.session_state['symptoms'] = symptoms
        st.session_state['urgency'] = urgency
        st.session_state['location'] = parsed_location
        
        with st.spinner("Analyzing with AI..."):
                try:
                    ai_output = get_gemini_response(symptoms, urgency, parsed_location)
                except Exception as exc:
                    ai_output = ""
                    error_text = str(exc)
                    st.error("⚠️ AI service unavailable. Please try again later.")
                    if "quota" in error_text.lower() or "resource_exhausted" in error_text.lower():
                        st.warning("Your Gemini API quota is exhausted or rate limited. Wait a moment and try again.")
                    st.write(f"Error details: {error_text}")
                    st.stop()
        
        # Display AI results
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        for line in ai_output.split('\n'):
            if "Emergency level" in line:
                st.markdown(f"🚨 **{line}**")
            elif "Should the patient call an ambulance" in line:
                st.markdown(f"🧠 **{line}**")
            elif "Possible condition" in line:
                st.markdown(f"🩹 **{line}**")
            elif "Immediate first aid" in line:
                st.markdown(f"🩹 **{line}**")
            elif "Safety advice" in line or "Warning" in line:
                st.markdown(f"⚠️ **{line}**")
            else:
                st.markdown(line)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Emergency actions
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if emergency_level == "Emergency":
                st.button("🚑 Call Ambulance (999)", use_container_width=True)
            else:
                st.button("🚑 Call Ambulance", use_container_width=True)
        with col2:
            st.button("🏥 Find Nearby Hospital", use_container_width=True)
        
        # === AI SUGGESTED DOCTORS & HOSPITALS SECTION ===
        st.markdown('<div class="section-title">🏆 AI Suggested Doctors & Specialists</div>', unsafe_allow_html=True)
        
        # Get all doctors data
        all_doctors = get_doctors_data()
        
        # Filter doctors based on symptoms
        filtered_doctors = filter_doctors_by_symptoms(symptoms, all_doctors)
        
        # Initialize session state for showing more doctors
        if 'show_all_doctors' not in st.session_state:
            st.session_state['show_all_doctors'] = False
        
        # Determine how many doctors to display
        doctors_to_display = filtered_doctors if not st.session_state['show_all_doctors'] else all_doctors
        display_count = len(doctors_to_display)
        
        # Display doctor cards
        st.write(f"**🩺 Recommended {len(filtered_doctors)} specialist(s) based on your symptoms:**")
        st.markdown("---")
        
        # Show first 3 doctors
        display_doctor_cards(doctors_to_display[:3])
        
        # Show More button
        if display_count > 3:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if not st.session_state['show_all_doctors']:
                    if st.button(f"📋 Show More Doctors ({display_count - 3} more)", use_container_width=True):
                        st.session_state['show_all_doctors'] = True
                        st.rerun()
                else:
                    if st.button("📋 Show Less", use_container_width=True):
                        st.session_state['show_all_doctors'] = False
                        st.rerun()
        
        # Display additional doctors if "Show More" was clicked
        if st.session_state['show_all_doctors'] and display_count > 3:
            st.markdown("---")
            remaining_doctors = doctors_to_display[3:]
            display_doctor_cards(remaining_doctors)

st.markdown('<div class="disclaimer">⚠️ This is AI guidance, not medical advice. For emergencies, call your local emergency number immediately.</div>', unsafe_allow_html=True)