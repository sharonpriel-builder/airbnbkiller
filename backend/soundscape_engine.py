import os
import streamlit as st
from openai import OpenAI
import qrcode
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI API client safely
openai_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_key)

# Create a local folder on the Streamlit server to hold audio files if it doesn't exist
AUDIO_DIR = "static_audio"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

def analyze_listing_and_write_script(image_url: str, host_name: str, city: str) -> str:
    system_prompt = (
        "You are an expert luxury Airbnb hospitality manager. Your job is to look at a property image "
        "and write a welcoming, high-end audio guide script for the check-in experience. "
        "The tone should be cool, warm, welcoming, and hyper-local. Write it entirely in ENGLISH. "
        "Include: A welcome message from the host, a description of the vibe, "
        "2-3 secret local recommendations in the neighborhood (cafes/bars), and a polite reminder to keep the place clean. "
        "Keep it concise, around 100-120 words maximum."
    )
    
    response = openai_client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"The host name is {host_name}, location is {city}. Write the script in English."},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        max_tokens=300
    )
    return response.choices[0].message.content

def generate_audio_guide_openai(script: str) -> bytes:
    response = openai_client.audio.speech.create(
        model="tts-1",           
        voice="nova",            
        input=script
    )
    return response.content


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
    
    # Try to load the file from the local server storage
    if filename:
        file_path = os.path.join(AUDIO_DIR, filename)
        if os.path.exists(file_path):
            st.markdown("<p style='text-align: center; font-weight: bold;'>Press play to listen to your guide:</p>", unsafe_allow_html=True)
            
            # Read and stream the file directly to the guest's phone
            with open(file_path, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
        else:
            st.error("The audio file has expired or was not found. Please ask the host to re-generate the QR code.")
    else:
        st.warning("No audio guide reference found in this link.")
        
    st.markdown("<p style='text-align: center; color: #555; margin-top: 100px; font-size: 0.8rem;'>Powered by Soundscape AI</p>", unsafe_allow_html=True)

else:
    # ==========================================
    # 🛠️ HOST DASHBOARD (מסך המארח)
    # ==========================================
    st.set_page_config(page_title="Soundscape AI Generator", page_icon="🎙️", layout="centered")
    
    st.title("🎙️ Soundscape AI Generator")
    st.subheader("Create premium welcome guides & QR codes instantly")
    
    host_name = st.text_input("Host Name", value="Tomer")
    city = st.text_input("Location / Neighborhood", value="Tel Aviv")
    image_url = st.text_input("Airbnb Listing Image URL", value="https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?q=80&w=1000&auto=format&fit=crop")
    
    if image_url:
        try: st.image(image_url, caption="Property Preview", use_column_width=True)
        except: st.warning("Could not load image preview.")
        
    if st.button("Generate Soundscape & QR ✨", type="primary"):
        if not openai_key:
            st.error("OpenAI API Key missing! Please configure it in Streamlit Secrets.")
        else:
            with st.spinner("🤖 AI is analyzing image and writing script..."):
                try:
                    # 1. Generate Script
                    script = analyze_listing_and_write_script(image_url, host_name, city)
                    st.success("📝 Script generated!")
                    st.text_area("Review Script", value=script, height=150)
                    
                    # 2. Generate Audio
                    with st.spinner("🎙️ Synthesizing premium audio..."):
                        audio_bytes = generate_audio_guide_openai(script)
                        st.audio(audio_bytes, format="audio/mp3")
                        
                    # 3. Save file locally on the Streamlit Server disk
                    clean_host = host_name.lower().strip().replace(' ', '_')
                    filename = f"{clean_host}_guide.mp3"
                    file_path = os.path.join(AUDIO_DIR, filename)
                    
                    with open(file_path, "wb") as f:
                        f.write(audio_bytes)
                        
                    # 4. Create dynamic clean link pointing to the local server file
                    base_url = "https://twinroute.streamlit.app" 
                    guest_link = f"{base_url}/?view=guest&host={host_name}&file={filename}"
                    
                    # 5. Generate QR Code
                    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
                    qr.add_data(guest_link)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    
                    # Convert QR to bytes
                    qr_buf = io.BytesIO()
                    qr_img.save(qr_buf, format="PNG")
                    qr_bytes = qr_buf.getvalue()
                    
                    # 6. Show QR Code to Host
                    st.write("---")
                    st.subheader("🖨️ Your Guest Welcome QR Code is Ready!")
                    st.image(qr_bytes, caption="Scan this with your phone to test the guest experience!", width=250)
                    
                    st.download_button(
                        label="Download QR Code PNG 💾",
                        data=qr_bytes,
                        file_name=f"{host_name}_welcome_qr.png",
                        mime="image/png"
                    )
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
