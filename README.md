# 🤖 Patient Communication AI Assistant

The **Patient Communication AI Assistant** is a Streamlit-based multilingual healthcare support system designed to help patients easily communicate with hospitals or medical services.  
Users can ask health-related questions and receive intelligent responses, with optional **Text-to-Speech** support via ElevenLabs API.

This project is developed as a **Mini Project** by **Tanishq Devagekar**.

---

## ✨ Features

- 🩺 AI-powered healthcare response system
- 🌐 Multilingual support (English, Kannada, Hindi and more planned)
- 🔊 Text-to-Speech with high-quality voice synthesis (ElevenLabs)
- 💬 User-friendly Streamlit interface
- 🔐 Secure API key management using `.env`
- 🔄 Modular and scalable design

---

## 🧱 Tech Stack

| Component | Technology |
|----------|------------|
| LLM / AI | Google Generative AI |
| Text-to-Speech | ElevenLabs API |
| Frontend UI | Streamlit |
| Programming Language | Python |
| Deployment | Local/Cloud-ready |

---

## 🚀 Getting Started

### 🔹 1️⃣ Clone the Repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```
###🔹 2. Create and Activate Virtual Environment
Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```
### 🔹 3. Install Required Packages
```bash
pip install -r requirements.txt
```
###🔹 4. Configure API Keys
Create a .env file in the project root directory and add your keys.

File: .env
```
GOOGLE_API_KEY=your_google_api_key_here

# ElevenLabs API Configuration (for Text-to-Speech)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# API Base URLs
ELEVENLABS_BASE_URL=[https://api.elevenlabs.io/v1](https://api.elevenlabs.io/v1)
```
⚠️ Note: Keep this file private. It is added to .gitignore to prevent uploading secrets to GitHub.

###🔹 5. Run the Application
```bash
streamlit run app/ui/streamlit.py
```
Once running, open the link provided in your terminal (usually http://localhost:8501).

###📂 Project Structure
```bash
.
├── app/
│   ├── ui/
│   │   └── streamlit.py        # Main UI script
│   ├── services/               # APIs & helper modules
│   │   ├── elevenlabs_service.py
│   │   └── ...
│   └── ...
├── uploads/                    # Optional folder for user uploads
├── test/                       # Optional testing scripts
├── requirements.txt            # Project dependencies
├── .env                        # API keys (NOT committed)
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation
└── venv/                       # Virtual environment (ignored)
```
###🛡️ Security Best Practices
✔ .env file stores sensitive API keys.

✔ Virtual environment (venv/) is not pushed to GitHub.

✔ No access tokens are hardcoded inside the source code.

✔ .gitignore is configured to handle private data.

###🧑‍⚕️ Use Cases
This AI system is designed for:

Basic Patient Queries: Answering common health questions.

Hospital Info Assistant: Guiding patients through services.

Symptom Guidance: Preliminary advice (non-diagnostic).

Multilingual Support: Breaking language barriers in healthcare.

###🚧 Future Enhancements
📱 WhatsApp Bot: Integration for real-time medical support.

🎧 Voice-to-Voice: Full conversational audio mode.

🏥 Hospital Integration: Connecting to appointment systems.

🌏 Expanded Languages: Support for more regional dialects.

🤝 Contributions
Pull requests and suggestions are welcome! If you encounter a bug or want a new feature, please create an Issue on GitHub.

👨‍💻 Author
🎓 Mini Project — Patient Communication AI Assistant

Developed by: Tanishq Devagekar

📌 Feel free to ⭐ Star the repo if you like the project!
