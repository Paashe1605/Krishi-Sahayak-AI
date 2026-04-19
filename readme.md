


```markdown
# 🌾 KisanMitra AI (Intelligent Digital Agronomist for Bharat)(Our this project is a PRE-EXISTING PROJECT WHICH WE HAVE FURTHER DEVELOPED ADDING VARIOUS OTHER USEFUL FEATURES )

> **"From a Simple Plant Doctor to a Forensic-Level Real-Time Agricultural Agent."**

**🌐 Live App:** [https://kisanmitra-app.onrender.com](https://kisanmitra-app.onrender.com)

---

## 📖 Table of Contents
- [🚀 Evolution: Before vs. Now](#-evolution-before-vs-now)
- [🚩 Problem Statement](#-problem-statement)
- [💡 Our Solution](#-our-solution)
- [✨ Key Features](#-key-features)
- [🛠 Tech Stack & Architecture](#-tech-stack--architecture)
- [📂 Project Structure](#-project-structure)
- [🚀 Local Installation](#-local-installation)
- [🔮 Future Roadmap](#-future-roadmap)
- [🤝 Contributors](#-contributors)

---

---

## 🚩 Problem Statement

Agriculture is the backbone of our economy, yet farmers face significant challenges:
1.  **Delayed Diagnosis:** Millions of tons of crops are lost annually due to incorrect or late detection of plant diseases.
2.  **Information Gap:** Access to expert Agronomists is expensive and rare in remote villages.
3.  **Language Barrier:** Most agri-tech tools are in English, alienating the rural population.
4.  **Static Data:** Existing apps provide outdated advice, not real-time market prices or current local officer contacts.

---


## 🚀 Evolution: Before vs. Now

We have transformed KisanMitra from a static diagnosis tool into a **Dynamic, Agentic Intelligence**. Here is how we upgraded the core architecture:

| Feature Category | ❌ Before (Standard Prototype) | ✅ NOW (KisanMitra 2.0 Agent) |
| :--- | :--- | :--- |
| **AI Intelligence** | Basic image classification & diagnosis. | **Forensic Pathologist Persona:** Identifies pathogen lifecycles, specific symptoms, and root causes. |
| **Data Accuracy** | Static training data (often outdated). | **Google Search Grounding:** Fetches **Real-Time** medicine prices and current availability from the live web. |
| **Local Support** | Generic advice (e.g., "Contact local officer"). | **Hyper-Local Intelligence:** Finds **Actual Names & Phone Numbers** of KVK officers in the user's specific district/village. |
| **Reliability** | Prone to crashes if AI output was malformed. | **Self-Healing Engine:** Automatically detects errors and retries with internal knowledge fallback. **100% Uptime.** |
| **Reporting** | Web-only view; hard to share. | **CEO-Level PDF Reports:** Auto-generates professional, printable PDFs with **Smart Image Resizing** & **Hybrid Layouts**. |
| **User Interface** | Standard text display. | **Immersive UI:** Neon product tags (Organic/Chemical), interactive video glow effects, and "breathing" animations. |


## 💡 Our Solution

**KisanMitra AI** is a **Multilingual, Voice-Enabled, Agentic AI** that acts as a 24/7 personal plant doctor. 

Unlike standard classifiers, it uses a **Forensic Pathologist Persona** grounded with **Google Search** to provide real-time cures, verified local contacts, and professional reports—all accessible via a simple photo.

---

## ✨ Key Features

### 1. 📸 Smart Input System (Camera & Location)
* **Live Camera Capture:** Farmers can take photos directly within the app or upload from the gallery.
* **Region-Specific Context:** Users select their **State/Region** (e.g., Gujarat, Bihar), ensuring the AI provides advice relevant to the local climate and available resources.

### 2. 🔍 Forensic Diagnosis (Agentic AI)
Powered by **Google Gemini 2.5 Flash**, the agent acts as a "Forensic Plant Pathologist."
* **Deep Analysis:** Identifies pathogen lifecycles, specific visual symptoms, and root causes.
* **Self-Healing Engine:** A robust backend that automatically detects data errors (JSON failures) and "heals" itself by retrying with internal knowledge, ensuring **100% reliability**.

### 3. 🌐 Real-Time Market Intelligence (Google Search)
The agent doesn't just guess; it **searches the live web** to provide:
* **Live Medicine Prices:** "Buy Now" links with current market availability.
* **Verified Local Experts:** Finds *actual* names and phone numbers of KVKs (Krishi Vigyan Kendras) and Agriculture Officers in the user's specific district.

### 4. 📄 Professional PDF Reports (Hybrid Layout)
Users can download a **High-Level Clickable Diagnostic Report** (`.pdf`):
* **Hybrid Layout Engine:** Automatically transforms from a **2x2 Grid (Web)** to a **Clean Vertical Stack (Print)** for better readability.
* **Smart Image Resizing:** Ensures user-uploaded crop photos are never stretched or distorted in the PDF.
* **Clickable Resources:** PDF links remain active, directing farmers to videos, maps, and purchase pages.

### 5. 🗣️ Vernacular Voice & Text Support
* **Multilingual:** Full support for **Hindi, English, Marathi, Gujarati, Tamil, Punjabi, and Bengali**.
* **Voice-First Design:** Includes **Speech-to-Text** (for queries) and **Text-to-Speech** (Audio Advice) so farmers can *listen* to the diagnosis.

### 6. 🎨 Immersive User Experience
* **Neon Product Tags:** Visual indicators for **Organic (Green)** vs **Chemical (Red)** remedies.
* **Interactive Glow:** Hover effects on video links to guide user interaction.
* **Breathing Loader:** A calming, organic animation during the analysis phase.

---

## 🛠 Tech Stack & Architecture

| Component | Technology |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 (Glassmorphism), JavaScript (Fetch API) |
| **Backend** | Python, Flask (Microservice Architecture) |
| **AI Brain** | **Google Gemini 2.5 Flash** (via Google GenAI SDK) |
| **Agent Tools** | **Google Search Tool** (Grounding), Brace-Counting Parser (Data Sanitization) |
| **Audio** | Edge-TTS (Neural High-Quality Voices), gTTS (Fallback) |
| **PDF Engine** | `html2pdf.js` (Client-side rendering with Hybrid Mode) |
| **Database** | SQLite (SQLAlchemy ORM) |

## 🤝 Powered by Google Technologies

KisanMitra AI is built on the robust **Google Cloud** and **AI ecosystem**, ensuring enterprise-grade reliability and intelligence.

| Technology | Usage in KisanMitra |
| :--- | :--- |
| **Google Gemini 2.5 Flash** | The core "Forensic Pathologist" brain. It analyzes crop images, detects diseases, and generates detailed treatment plans with high speed and accuracy. |
| **Google Search Grounding (Vertex AI)** | Connects the frozen AI model to the live internet. It fetches **real-time prices** of medicines and finds **verified contact numbers** of local Agriculture Officers. |
| **Google Cloud Vertex AI** | The managed machine learning platform that hosts and serves the Gemini model, ensuring low latency and high availability. |
| **Google Text-to-Speech (gTTS)** | Powers the vernacular audio advice, allowing farmers to listen to the diagnosis in their native language (Hindi, Gujarati, etc.). |
| **Google Maps** | Integrated into the "Local Experts" section to provide farmers with direct navigation links to nearby Krishi Vigyan Kendras (KVKs). |

---

## 📂 Project Structure

```bash
KisanMitra/
├── app.py                 # Main Flask Application (Routes & Logic)
├── kisan_agent.py         # AI Brain (Search Tool, Self-Healing Parser, Prompt Engineering)
├── models.py              # Database Schema (Users, Diagnosis History)
├── requirements.txt       # Dependencies (Flask, Google-GenAI, etc.)
├── static/
│   ├── uploads/           # User uploaded images
│   └── audio/             # Generated MP3 advice
└── templates/
    ├── index.html         # Camera/Upload UI with Location & Breathing Loader
    └── result.html        # The "CEO-Level" Dashboard & Hybrid PDF Engine

```

---


## 🔮 Future Roadmap

* **Offline Mode:** Lightweight TFLite model for areas with zero internet connectivity.
* **More Enhanced Version For Smartphone:** Enhanced versions of the app for smartphone(It currently works though.).
* **Cattel Sahayak:** Similar Agent Integrated for Cattle.
* **Drone Integration:** API support for aerial imagery analysis.
* **Community Forum:** A peer-to-peer network for farmers to discuss issues.
* **IoT Sensors:** Integration with soil moisture and NPK sensors.

---

## 🤝 Contributors

* **PAARAS SHEMRUDKAR** - *Lead Developer / AI Architect / System Design / Research / Market Analysis*
* **PRACHI SHARMA** - *UI/UX Design / Research / Quality Assurance*
* **YASHKUMAR BHOI** - *Testing / Research / Market Analysis*


---

<div align="center">
<b>Made with ❤️ for Indian Farmers (Annadata) 🌾</b>

<i>"Technology that touches the soil."</i>
</div>

## License & Copyright

© 2026 Paaras Shemrudkar & Prachi Sharma (Owners of KisanMitra AI). All rights reserved.

This project is proprietary software. You may not use, copy, modify, or distribute the code in this repository without express written permission from the owners.

```

```