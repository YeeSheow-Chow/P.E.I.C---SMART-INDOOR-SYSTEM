# P.E.I.C---SMART-INDOOR-SYSTEM
An intelligent indoor control system combining mmWave radar and YOLO-based sensing for privacy-aware, energy-efficient public space management.
# PEIC: Privacy-First Efficient Indoor Control

PEIC is an intelligent indoor control system designed for smart public spaces. It integrates **mmWave radar sensing** and **YOLO-based visual detection** to achieve occupancy-aware control of **lighting** and **air-conditioning (HVAC)** with a privacy-first and energy-efficient design philosophy.

This project was developed as an academic/research-oriented prototype for demonstrating how multi-sensor fusion can improve indoor automation in spaces such as classrooms, offices, libraries, and other shared environments.

---

## Overview

Traditional indoor control systems often rely on fixed schedules, manual operation, or single-sensor triggers, which may lead to wasted energy and limited environmental adaptability.  
PEIC addresses this problem by combining:

- **mmWave radar** for low-latency motion and presence sensing
- **YOLO-based camera detection** for more reliable occupancy understanding
- **Sensor fusion logic** for robust decision-making
- **Occupancy-aware control** for lighting and HVAC
- **Privacy-first design** to reduce unnecessary visual activation
- **Energy-conscious operation** for more sustainable indoor environments

The goal of the project is to create a smarter and more responsive indoor control framework that balances **privacy**, **comfort**, and **energy efficiency**.

---

## Key Features

- **Occupancy Detection**
  Detects indoor presence and human activity using mmWave radar and computer vision.

- **Sensor Fusion**
  Combines radar and camera information for more reliable detection than a single-sensor system.

- **Lighting Control**
  Adjusts lighting state based on room occupancy.

- **HVAC Control**
  Supports occupancy-aware air-conditioning control to reduce unnecessary energy consumption.

- **Privacy-First Logic**
  Uses mmWave sensing as a primary trigger to reduce excessive or unnecessary camera usage.

- **Energy Efficiency**
  Improves environmental control decisions for smarter public-space management.

---

## System Architecture

The project consists of the following major components:

- **mmWave Radar Module**
  Used for human presence and motion sensing.

- **Camera + YOLO Detection**
  Used for visual occupancy analysis when needed.

- **Microcontroller / Embedded Control Layer**
  Handles data communication and device actuation.

- **Control Logic**
  Processes sensing results and determines lighting/HVAC actions.

- **Web Interface**
  Provides a visual presentation of the project concept, system pages, and status displays.

---

## Application Scenarios

PEIC is designed for shared indoor environments such as:

- Classrooms
- Offices
- Libraries
- Meeting rooms
- Other public or semi-public indoor spaces

---

## Tech Stack

Depending on the current branch or module, this project may include:

- **Frontend:** HTML, CSS, JavaScript
- **Detection / Vision:** Python, YOLO
- **Embedded / Hardware Integration:** Arduino / ESP32 / related modules
- **Sensors:** mmWave radar
- **Prototype Website / UI Design:** modern responsive web interface for system presentation

---

## Repository Structure

Example structure:

```bash
.
├── index.html
├── style.css
├── script.js
├── assets/
│   ├── images/
│   └── icons/
├── docs/
├── hardware/
├── models/
└── README.md
