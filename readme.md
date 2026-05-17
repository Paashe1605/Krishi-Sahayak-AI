<div align="center">

# 🌾 Krishi Shayak AI 🌾
### *The Unified Platform for India's Smart Farming Ecosystem*

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](#)
[![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?style=for-the-badge&logo=flask)](#)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-3.1%20Flash%20Lite-orange?style=for-the-badge&logo=google)](#)
[![Vertex AI](https://img.shields.io/badge/GCP-Vertex%20AI-blue?style=for-the-badge&logo=googlecloud)](#)
[![Live on Render](https://img.shields.io/badge/Deployed-Live_on_Render-brightgreen?style=for-the-badge&logo=render)](#)

*An enterprise-grade, multi-modal, multilingual, and voice-enabled agricultural AI platform.* <br>
**Evolved from KisanMitra — Built by Tech Surfers (Paaras Shemrudkar & Prachi Sharma)**

[🌍 Launch Live Web App](https://kisanmitra-app.onrender.com) • [Explore Features](#-the-four-pillars-of-krishi-shayak) • [System Architecture](#-core-platform-capabilities) • [Tech Stack](#-technology-stack) 

</div>

---

## 🌟 About The Project
**Krishi Shayak AI** is a state-of-the-art agricultural ERP and diagnostic platform designed to empower Indian farmers. Evolving far beyond a simple crop-scanning app, Krishi Shayak is a completely decoupled, chained-inference AI ecosystem consisting of **four specialized AI agents**. 

From detecting cattle diseases to fetching live IMD weather alerts and generating localized financial insurance plans, Krishi Shayak acts as a Master Agronomist, Veterinarian, and Financial Advisor—accessible seamlessly in **10 Indian regional languages**.

🚀 **Experience the platform live right now:** [https://kisanmitra-app.onrender.com](https://kisanmitra-app.onrender.com)

---

## 🏛️ The Four Pillars of Krishi Shayak

<div align="center">
  <table>
    <tr>
      <td align="center" width="50%">
        <h3>🌱 KisanShayak AI</h3>
        <i>The Personal Crop Doctor</i><br><br>
        Upload an image of a diseased crop or describe the issue via Voice. The AI scans the flora to provide <b>Organic & Chemical remedies</b>, survival timelines, required products, and YouTube setup tutorials.
      </td>
      <td align="center" width="50%">
        <h3>🐄 Pashu Sahayak AI</h3>
        <i>The Livestock Guardian</i><br><br>
        A dedicated veterinary agent for cattle health. It analyzes animal symptoms, provides <b>Ethnoveterinary & Pharmaceutical cures</b>, and establishes crucial Herd Safety and Quarantine protocols.
      </td>
    </tr>
    <tr>
      <td align="center" width="50%">
        <h3>🛡️ Krishi Rakshak</h3>
        <i>The Financial Shield</i><br><br>
        Upload a PDF/Image of any diagnosis report. The AI acts as an actuary, calculating the <b>Financial Health Score</b>, estimated recovery costs, and mapping the farmer to eligible <b>Govt Insurance Schemes (PMFBY)</b>.
      </td>
      <td align="center" width="50%">
        <h3>🌍 Dharti Chakra</h3>
        <i>Weather, Geology & Alerts</i><br><br>
        Analyzes soil images and GPS coordinates using <b>Live Google Search</b> to fetch IMD weather alerts. Includes the revolutionary <b>"Kheti Ayojan"</b> feature—a chained AI inference that generates a custom step-by-step farming plan based on land size.
      </td>
    </tr>
  </table>
</div>

---

## 🚀 Core Platform Capabilities

### 🗣️ The Polyglot Engine (100% Native i18n)
Zero English bleed-through. The entire platform—from UI buttons to dynamic AI JSON responses—is natively translated via a custom `translations.js` dictionary and strict LLM prompting.
Supported: *English, Hindi, Gujarati, Marathi, Tamil, Telugu, Bengali, Punjabi, Kannada, Malayalam.*

### 🎙️ Multi-Modal Input & Audio Output
* **Input:** Farmers can type, upload Images/PDFs, use the device Camera, or dictate via the **Web Speech API**.
* **Output:** Every report dynamically generates a localized MP3 summary using **EdgeTTS/gTTS**, playable directly inside the browser.

### 🧠 Chained AI Inference (Kheti Ayojan)
Dharti Chakra utilizes an advanced background AJAX architecture. The output of the primary Weather/Soil AI is fed *directly* into a secondary Agronomist AI prompt alongside user inputs (Land Size/Crops) to generate a hyper-specific, actionable **Farming Plan** without reloading the page.

### 🌐 Google Search Grounded
Agents are powered by Vertex AI with `use_search=True`, allowing them to bypass LLM hallucinations by actively scraping the web for Live IMD Weather Warnings, Current Agri-News, and localized NGO/Expert contacts.

### 📄 One-Click PDF Export
Powered by `html2pdf.js`, farmers can download highly-styled, printable PDF versions of any agent's report with a single tap, complete with dynamic layout adjustments.

---

## 🌍 Live Deployment

Krishi Shayak AI is hosted securely in the cloud and requires zero installation or local setup. The platform is accessible globally from any modern smartphone or desktop browser.

👉 **[Launch Krishi Shayak AI (Live Web App)](https://kisanmitra-app.onrender.com)**

---

## 💻 Technology Stack

| Category | Technologies |
| :--- | :--- |
| **Frontend Architectures** | HTML5, CSS3 (Custom Glassmorphism), Vanilla JavaScript, Bootstrap (Navbar) |
| **Backend Framework** | Python 3.9+, Flask, Werkzeug, SQLite3 (SQLAlchemy/Native) |
| **AI & Machine Learning** | Google Gemini 3.1 Flash-Lite Preview, Google Cloud Vertex AI SDK |
| **Data Processing & Utilities** | PyMuPDF (`fitz`) for Silent PDF Compression, Pillow (`PIL`) for Image Optimization |
| **APIs & Integrations** | EdgeTTS (Audio Synth), HTML2PDF, Web Speech API |

---

---

## 👨‍💻 The Team (Tech Surfers)

* **Paaras Shemrudkar** - *System Ideation & Lead - Backend / AI Architect & Orchrestator*
* **Prachi Sharma** - *Lead UI/UX Architect & Frontend Developer, Q&A*

---

<div align="center">
  <p><b>Built with ❤️ and <i>Khoon Pasina</i> for the Farmers of India.</b></p>
  <p><a href="https://kisanmitra-app.onrender.com">Start using Krishi Shayak AI today.</a></p>
  <p>© 2026 Tech Surfers. All rights reserved.</p>
</div>