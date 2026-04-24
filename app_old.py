import streamlit as st
from dotenv import load_dotenv
import os
from utils import get_gemini_response, get_coordinates, find_nearby_hospitals, get_hospital_details, get_directions, calculate_distance

# Load environment variables
load_dotenv()

# Custom CSS
with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- UI ---
st.markdown('<div class="hero-title">Emergency AI Health Support</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Describe your symptoms and get instant AI-powered emergency guidance.</div>', unsafe_allow_html=True)

with st.form("symptom_form"):
    symptoms = st.text_area("Describe your symptoms", max_chars=500, height=120)
    urgency = st.selectbox("Urgency level", ["Low", "Medium", "High"])
    location = st.text_input("Your location (city, postcode, or full address)")
    submitted = st.form_submit_button("Analyze Symptoms")

ai_output = ""
emergency_level = ""
if submitted and symptoms.strip():
    with st.spinner("Analyzing with AI..."):
        ai_output = get_gemini_response(symptoms, urgency, location)
    
    # Parse emergency level
    for line in ai_output.split('\n'):
        if "Emergency level" in line.lower():
            if "emergency" in line.lower():
                emergency_level = "Emergency"
            elif "urgent" in line.lower():
                emergency_level = "Urgent"
            else:
                emergency_level = "Normal"
            break
    
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
        if location:
            if st.button("🏥 Find Nearby Hospitals", key="find_hospitals", use_container_width=True):
                st.session_state['show_hospitals'] = True
        else:
            st.info("Enter location to find hospitals")

# Hospital finder section
if st.session_state.get('show_hospitals', False) and location:
    lat, lng = get_coordinates(location)
    if lat and lng:
        hospitals = find_nearby_hospitals(lat, lng)
        if hospitals:
            st.markdown("### 🏥 Nearby Hospitals")
            for i, hospital in enumerate(hospitals):
                distance = calculate_distance(lat, lng, hospital['lat'], hospital['lng'])
                phone = get_hospital_details(hospital['place_id'])
                dist, time = get_directions(lat, lng, hospital['lat'], hospital['lng'])
                
                st.markdown('<div class="hospital-card">', unsafe_allow_html=True)
                st.markdown(f"**{hospital['name']}**")
                st.markdown(f"📍 {hospital['address']}")
                st.markdown(f"⭐ Rating: {hospital['rating']} | 📏 Distance: {distance} km")
                if phone != 'Contact not available':
                    st.markdown(f"📞 {phone}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if phone != 'Contact not available':
                        st.button(f"📞 Call {hospital['name']}", key=f"call_{i}")
                    else:
                        st.button("📞 Contact Not Available", disabled=True, key=f"no_call_{i}")
                with col2:
                    maps_url = f"https://www.google.com/maps/dir/{lat},{lng}/{hospital['lat']},{hospital['lng']}"
                    st.link_button(f"🗺️ View Route ({dist}, {time})", maps_url, key=f"route_{i}")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("No hospitals found nearby. Please check your location.")
    else:
        st.error("Could not geocode the location. Please enter a valid address.")

st.markdown('<div class="disclaimer">⚠️ This is AI guidance, not medical advice. For emergencies, call your local emergency number immediately.</div>', unsafe_allow_html=True)