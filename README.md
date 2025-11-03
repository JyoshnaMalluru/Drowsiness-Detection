# Drowsiness-Detection

A real-time system to monitor eye closure and detect drowsiness or fatigue. The system tracks eyes using computer vision and raises alerts when prolonged closure is detected.

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Acknowledgements](#acknowledgements)
---

## Overview
Drowsiness-Detection focuses on **eye tracking** to identify signs of fatigue. By monitoring eye closure duration in real-time, it can alert the user to prevent accidents.

---

## Features
- Real-time eye detection using **OpenCV**.
- Detects prolonged eye closure.
- Audible or visual alert when drowsiness is detected.
- Works with a standard webcam.
- Simple and lightweight implementation.

---

## Technology Stack
- **Programming Language:** Python 3.x
- **Libraries:** 
  - [OpenCV](https://opencv.org/) – Eye detection and tracking.
  - [dlib](http://dlib.net/) – Optional: facial landmark detection for more precise tracking.
  - [NumPy](https://numpy.org/) – Numerical operations.
  - [imutils](https://github.com/jrosebr1/imutils) – Image processing helper functions.

---

## Installation
1. Clone the repository:  
```bash
git clone https://github.com/yourusername/Drowsiness-Detection.git
```
2. Navigate to the project folder:

```bash
cd Drowsiness-Detection
```
3. Create a virtual environment (optional):
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

4. Install required packages:
```bash
pip install -r requirements.txt
```
## Usage

1. Run the main script:
``` bash
python eye_drowsiness_detection.py
```

2. The webcam feed will open. The system will track your eyes in real-time.

3. If drowsiness is detected, an alert will be triggered.

4. Press Spacebar to exit.

## Acknowledgements

Inspired by OpenCV tutorials for eye tracking and drowsiness detection.

Uses real-time computer vision techniques to monitor eye closure.
