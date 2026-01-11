# 🌾 KisanMitra AI (Plant Pathologist & Agronomist Companion Agent)

> **Empowering Farmers with AI-Driven Crop Diagnosis & Multilingual Support.**

**🌐 Live App:** [https://kisanmitra-app.onrender.com](https://kisanmitra-app.onrender.com)

---

## 📖 Table of Contents
- [Problem Statement](#-problem-statement)
- [Our Solution](#-our-solution)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Local Installation](#-local-installation-guide)
- [Deployment](#-deployment)
- [Future Roadmap](#-future-roadmap)

---

## 🚩 Problem Statement

Agriculture is the backbone of our economy, yet farmers face significant challenges:
1.  **Crop Diseases:** Millions of tons of crops are lost annually due to delayed or incorrect diagnosis of plant diseases.
2.  **Lack of Expertise:** Access to agricultural experts (Agronomists) is expensive and often unavailable in remote areas.
3.  **Language Barrier:** Most digital tools are in English, making them inaccessible to the average rural farmer.
4.  **Resource Scarcity:** Farmers often don't know where to buy the correct organic or chemical remedies near them.

---

## 💡 Our Solution

**KisanMitra AI** is an intelligent plant disease diagnosis tool designed to bridge the gap between technology and traditional farming. 

It acts as a **24/7 Digital Agronomist** that fits in a farmer's pocket. By simply uploading a photo of a crop, the farmer gets an instant diagnosis, treatment plan, and resources—all in their local language.

---

## ✨ Key Features

### 1. 🔍 Instant Image Diagnosis
Powered by **Google Gemini 2.5 Flash**, the app analyzes plant leaves to detect diseases with high accuracy. It identifies the issue, the cause, and provides both organic and chemical solutions.

### 2. 🗣️ Multilingual Voice & Text Support
We believe technology should speak the farmer's language. The app fully supports:
* **Hindi** (हिंदी)
* **English**
* **Marathi** (मराठी)
* **Tamil** (தமிழ்)
* **Gujarati** (ગુજરાતી)

Includes **Voice Input** (Speech-to-Text) and **Audio Output** (Text-to-Speech) for accessibility.

### 3. 📊 Smart 2x2 Result Dashboard
The results are presented in a clean, structured 2x2 grid:
* **Diagnosis:** Detailed, bullet-point analysis (justified text with scroll).
* **Statistics:** Visual charts showing Health Score, Infection Severity, and AI Confidence.
* **Video Remedies:** Curated YouTube search links for visual treatment guides.
* **Buy Medicines:** Direct links to purchase recommended products near the user.

### 4. 🎨 User Experience
* **"Breathe" Loader:** A calming, organic animation during analysis.
* **Responsive Design:** Works perfectly on mobile devices (where farmers need it most).

---

## 🛠 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 (Flexbox/Grid), JavaScript, Chart.js |
| **Backend** | Python, Flask |
| **AI Model** | Google Gemini 2.0 Flash (via Google GenAI SDK) |
| **Database** | SQLite (via SQLAlchemy) |
| **Audio/Voice** | gTTS (Google Text-to-Speech), Web Speech API |
| **Deployment** | Render (Gunicorn Server) |

---

## 📂 Project Structure

```bash
KisanMitra/
├── app.py                 # Main Flask Application
├── kisan_agent.py         # AI Logic (Gemini API Integration)
├── models.py              # Database Models (SQLAlchemy)
├── requirements.txt       # Project Dependencies
├── Procfile               # Render Deployment Command
├── static/
│   ├── uploads/           # User uploaded images
│   └── audio/             # Generated audio files
└── templates/
    ├── index.html         # Home Page (Upload & Voice Input)
    └── result.html        # Analysis Dashboard (2x2 Grid)

```

---

## 💻 Local Installation Guide

Want to run this project on your own machine? Follow these steps:

**1. Clone the Repository**

```bash
git clone [https://github.com/Paashe1605/KisanMitra.git](https://github.com/Paashe1605/KisanMitra.git)
cd KisanMitra

```

**2. Create a Virtual Environment**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

```

**3. Install Dependencies**

```bash
pip install -r requirements.txt

```

**4. Set Up Environment Variables**
Create a file named `.env` in the root folder and add your Google Gemini API Key:

```env
GOOGLE_CLOUD_PROJECT=your_cloud_project_id_here
GOOGLE_CLOUD_LOCATION=us-central1
```

**5. Run the Application**

```bash
python app.py

```

Open your browser and visit: `http://127.0.0.1:5000`

---

## 🚀 Deployment

This project is deployed on **Render** using a Gunicorn server.

* **Platform:** Render Free Tier
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `gunicorn app:app`
* **Environment Variables:** `Cloud json api file and the .env variables set in Render dashboard.

---

## 🔮 Future Roadmap

* **Community Forum:** Allow farmers to discuss issues with peers.
* **Weather Integration:** Real-time weather alerts based on location.
* **Drone Integration:** API support for drone imagery analysis.
* **Offline Mode:** Lightweight TFLite model for areas with no internet.

---

## 🤝 Contributors

* **PAARAS SHEMRUDKAR** - *Lead Developer / AI Logic*
* **PRACHI SHARMA** - *UI/UX{Frontend & Design} / Testing*

---

Made with ❤️ for Indian Farmers & Agri Buisness Owners🌾@ AUTONOMOUS HACKS 2026

```

```