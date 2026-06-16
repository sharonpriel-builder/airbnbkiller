# airbnbkiller

## 🎙️ Soundscape AI: Premium Airbnb Audio Guides

**Soundscape AI** is a smart, automated SaaS tool designed for luxury Airbnb hosts to elevate their guest check-in experience. By leveraging cutting-edge Generative AI, the platform transforms a single property image into a cinematic, hyper-local audio welcome guide that guests can listen to upon arrival.

### ✨ Key Features
* **AI Property Analysis (Vision):** Seamlessly analyzes Airbnb listing images using OpenAI's `gpt-4o` to understand the unique vibe, design, and aesthetic of the property.
* **Hyper-Local Script Writing:** Dynamically generates a welcoming, warm, and highly personalized welcome script in English. The script includes host introductions, property rules (cleanliness reminders), and 2-3 secret neighborhood recommendations (cafes, bars, hidden gems).
* **Cinematic Voice Synthesis:** Converts the generated script into high-quality, professional, and natural-sounding audio using OpenAI's advanced Text-to-Speech (TTS) engine.
* **Instant QR Code Generation:** Automatically generates a branded QR code for the host. Hosts can print and place the QR code inside the apartment (e.g., on the fridge or welcome table).
* **Dual-Sided Streamlit UI:** A single, lightweight application that serves two distinct experiences:
  1. **Host Dashboard:** For generating the guides and downloading the QR codes.
  2. **Guest Landing Page:** A minimalist, premium mobile-responsive view triggered automatically when a guest scans the physical QR code to play their audio guide.

### 🛠️ Tech Stack
* **Frontend/Backend:** [Streamlit](https://streamlit.io/) (Python-based web framework)
* **AI Capabilities:** OpenAI API (`gpt-4o` for Vision/Text, `tts-1` for audio synthesis)
* **QR Utilities:** `qrcode` (Python library for dynamic URL encoding)
* **Environment Management:** `python-dotenv`

---

### 🚀 Quick Start & Deployment

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/sharon-priel/twinroute.git](https://github.com/sharon-priel/twinroute.git)
   cd twinroute
