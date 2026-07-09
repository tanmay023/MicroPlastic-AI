# 🔬 MicroPlastic-AI

An AI-powered desktop application for automated microplastic detection and analysis using YOLO11 and Computer Vision.

---

## 📌 Overview

MicroPlastic-AI is a desktop application developed to detect and analyze microplastic particles from microscopic images. It combines YOLO11 object detection with image analysis techniques to generate particle statistics, density estimation, visualizations, and automated reports.

---

## ✨ Features

* YOLO11-based microplastic detection
* Particle analysis (Area, Width, Height, Aspect Ratio, Diameter)
* Density estimation
* Statistical analysis
* Scientific visualizations
* HTML, CSV and JSON report generation
* Batch image processing
* Interactive Tkinter desktop GUI

---

## 🛠 Technology Stack

* Python 3.11
* Ultralytics YOLO11
* PyTorch
* OpenCV
* NumPy
* Pandas
* Matplotlib
* Tkinter

---

## 📂 Project Structure

```
MicroPlastic-AI/
│
├── dataset/
├── microplastic_ai/
├── models/
├── outputs/
├── docs/
├── tests/
├── requirements.txt
└── main.py
```

---

## 🚀 Installation

Clone the repository

```bash
git clone https://github.com/tanmay023/MicroPlastic-AI.git
cd MicroPlastic-AI
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment

Windows

```bash
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python main.py
```

---

## 📊 Outputs

The application generates:

* Detection Images
* Particle Statistics
* Density Estimation
* Histograms & Heatmaps
* HTML Report
* CSV Report
* JSON Report

---

## 🔬 Future Work

* Multi-class microplastic classification
* Explainable AI (Grad-CAM)
* Real-time detection
* Raspberry Pi & IoT deployment
* Cloud dashboard integration
---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.
