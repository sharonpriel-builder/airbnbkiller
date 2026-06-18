import os
import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS
import qrcode
import io
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini API client correctly for a standard API Key
gemini_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
if gemini_key:
    # Passing the api_key directly here prevents the OAuth2/Access Token error
    ai_client = genai.Client(api_key=gemini_key)
else:
    ai_client = None

# Create local folder for audio files
AUDIO_DIR = "static_audio"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

def analyze_listing_with_gemini(image_url: str, host_name: str, city: str) -> str:
    if not ai_client:
        raise Exception("Gemini API Key is missing from configuration.")
        
    system_prompt = (
        "You are an expert luxury Airbnb hospitality manager. Look at this property image "
        "and write a welcoming, high-end audio guide script for the check-in experience. "
        "The tone should be cool, warm, welcoming, and hyper-local. Write it entirely in ENGLISH. "
        "Include: A welcome message from the host, a description of the vibe, "
        "2-3 secret local recommendations in the neighborhood (cafes/bars), and a polite reminder to keep the place clean. "
        "Keep it concise, around 100-120 words maximum. "
        "CRITICAL: Write ONLY words that should be spoken out loud. Do NOT include any sound effects, "
        "stage directions, music cues, or text inside brackets like (Sound of music) or [Ambient music]. "
        "The script must be 100% pure spoken text."
    )
    
    # Download the image bytes from the URL
    try:
        img_response = requests.get(image_url)
        img_response.raise_for_status()
        img_bytes = img_response.content
    except Exception as e:
        raise Exception(f"Failed to fetch image from URL: {e}")

    # Using the updated, long-term supported gemini-2.5-flash model
    response = ai_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            system_prompt,
            f"Host Name: {host_name}, Location: {city}.",
            types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg')
        ]
    )
    return response.text

def generate_audio_gtts(script: str) -> bytes:
    # 100% free TTS engine
    tts = gTTS(text=script, lang='en', tld='com', slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()


# --- DYNAMIC ROUTING VIA QUERY PARAMETERS ---
query_params = st.query_params

if "view" in query_params and query_params["view"] == "guest":
    # ==========================================
    # 🎉 GUEST LANDING PAGE (מסך האורח)
    # ==========================================
    st.set_page_config(page_title="Welcome to Your Stay", page_icon="🔑", layout="centered")
    
    host = query_params.get("host", "Your Host")
    filename = query_params.get("file", None)
    
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>✨ Welcome to Your Stay!</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #aaa; font-size: 1.2rem;'>A special audio welcome guide from <b>{host}</b></p>", unsafe_allow_html=True)
    st.write("---")
    
    if filename:
        file_path = os.path.join(AUDIO_DIR, filename)
        if os.path.exists(file_path):
            st.markdown("<p style='text-align: center; font-weight: bold;'>Press play to listen to your guide:</p>", unsafe_allow_html=True)
            with open(file_path, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
        else:
            st.error("Audio guide file not found on server.")
    else:
        st.warning("No audio guide found.")

else:
    # ==========================================
    # 🛠️ HOST DASHBOARD (מסך המארח)
    # ==========================================
    st.set_page_config(page_title="Soundscape AI Generator", page_icon="🎙️", layout="centered")
    
    st.title("🎙️ Soundscape AI (Gemini Edition) 🚀")
    st.subheader("Create 100% free welcome guides instantly")
    
    host_name = st.text_input("Host Name", value="Tomer")
    city = st.text_input("Location / Neighborhood", value="Tel Aviv")
    image_url = st.text_input("Airbnb Listing Image URL", value="https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?q=80&w=1000&auto=format&fit=crop")
    
    if image_url:
        try: st.image(image_url, caption="Property Preview", use_column_width=True)
        except: st.warning("Could not load image preview.")
        
    if st.button("Generate Soundscape & QR ✨", type="primary"):
        if not gemini_key:
            st.error("Gemini API Key missing! Please configure GEMINI_API_KEY in Streamlit Secrets.")
        else:
            with st.spinner("🤖 Gemini is analyzing image and writing script..."):
                try:
                    # 1. Generate Script via Gemini
                    script = analyze_listing_with_gemini(image_url, host_name, city)
                    st.success("📝 Script generated by Gemini!")
                    st.text_area("Review Script", value=script, height=150)
                    
                    # 2. Generate Audio via free gTTS
                    with st.spinner("🎙️ Synthesizing free google audio..."):
                        audio_bytes = generate_audio_gtts(script)
                        st.audio(audio_bytes, format="audio/mp3")
                        
                    # 3. Save file locally on the server
                    clean_host = host_name.lower().strip().replace(' ', '_')
                    filename = f"{clean_host}_guide.mp3"
                    file_path = os.path.join(AUDIO_DIR, filename)
                    
                    with open(file_path, "wb") as f:
                        f.write(audio_bytes)
                        
                    # 4. Create dynamic link pointing to your actual live server
                    base_url = "https://airbnbkiller-8ih343gqgj5auvybmfusrj.streamlit.app" 
                    guest_link = f"{base_url}/?view=guest&host={host_name}&file={filename}"
                    
                    # 5. Generate QR Code
                    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
                    qr.add_data(guest_link)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    
                    qr_buf = io.BytesIO()
                    qr_img.save(qr_buf, format="PNG")
                    qr_bytes = qr_buf.getvalue()
                    
                    # 6. Show QR Code
                    st.write("---")
                    st.subheader("🖨️ Your Guest Welcome QR Code is Ready!")
                    st.image(qr_bytes, caption="Scan this with your phone!", width=250)
                    
                    st.download_button(
                        label="Download QR Code PNG 💾",
                        data=qr_bytes,
                        file_name=f"{host_name}_welcome_qr.png",
                        mime="image/png"
                    )
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
