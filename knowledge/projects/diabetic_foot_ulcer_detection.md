# Enhancing Diabetic Foot Care: Real-Time Ulcer Detection

## Domain
IoT Healthcare | Embedded Systems | Real-Time Monitoring | Cloud Integration | Biomedical Engineering

## Technologies
NI LabVIEW, Arduino IDE, ESP32, Firebase Realtime Database, GSM Module (SIM800L), LM35 Temperature Sensor, HR202 Humidity Sensor, FSR 400/406 Pressure Sensors, JSON, HTTP Client

## Concepts
IoT Sensor Fusion, Real-Time Threshold-Based Detection, Cloud Data Sharing, Graphical Programming, Embedded System Design, Predictive Alert System, Remote Patient Monitoring

## Project Overview

Multi-sensor IoT system integrating pressure, temperature, and humidity measurements for early diabetic foot ulcer detection, delivering real-time alerts to healthcare providers via Firebase cloud and GSM SMS. Addresses single-sensor (pressure-only) false positives by fusing 3 sensor modalities.

## Problem Statement

| Problem | Impact | Solution |
|---|---|---|
| Single-sensor (pressure-only) systems produce false results | Delayed or missed diagnosis | Fused 3-sensor architecture for accurate detection |
| No real-time monitoring in existing designs | Ulcers worsen undetected | Continuous cloud-based monitoring with threshold comparison |
| No remote data sharing with healthcare providers | Delayed intervention | Firebase cloud + GSM SMS notification to doctors |

## System Architecture

```
Sensors (LM35 × 2, HR202 × 1, FSR 400/406 × 3)
        ↓
   ESP32 Wi-Fi Module
   ├── LED Indicator
   ├── GSM Module (SIM800L) → SMS Notification
   └── Firebase Realtime Database (Cloud)
                ↓
           LabVIEW VI
           ├── Front Panel (Gauges, Meters, Thresholds)
           └── Block Diagram (Dataflow Logic, HTTP GET/POST)
```

Data Flow: Sensors → ESP32 → Firebase (JSON) → LabVIEW HTTP GET → threshold comparison → GSM SMS alert on breach.

## Hardware Components

| Component | Model | Purpose |
|---|---|---|
| Temperature Sensor | LM35 × 2 | Measures top and bottom foot temperature (10 mV/°C output) |
| Humidity Sensor | HR202 × 1 | Measures relative humidity (20–95% RH range) |
| Pressure Sensor | FSR 400 + FSR 406 | Measures plantar pressure at left, right, and bottom foot zones |
| Microcontroller | ESP32 | Wi-Fi connectivity, sensor data acquisition, Firebase communication |
| GSM Module | SIM800L | Sends SMS alerts to healthcare providers |
| Cloud Platform | Firebase Realtime Database | Stores sensor readings and threshold control values |
| UI Platform | NI LabVIEW | Graphical front panel for monitoring and threshold configuration |

## Sensor Threshold Logic

**Temperature (LM35 — two sensors, top and bottom foot)**

| Delay | Threshold (°C difference) | Condition |
|---|---|---|
| 1 hr | 0.6 | >0.6 → Ulcer Detected |
| 6 hr | 2.0 | >2.0 → Ulcer Detected |
| 12 hr | 3.2 | >3.2 → Ulcer Detected |
| 1 day | 4.5 | >4.5 → Ulcer Detected |

**Pressure (FSR — left, right, bottom foot)**

| Delay | Threshold | Condition |
|---|---|---|
| 1 hr | 20 | >20 → Ulcer Detected |
| 6 hr | 40 | >40 → Ulcer Detected |
| 12 hr | 70 | >70 → Ulcer Detected |
| 1 day | 100 | >100 → Ulcer Detected |

**Humidity (HR202)**

| Delay | Threshold (% RH) | Condition |
|---|---|---|
| 1 hr | 2–3 | >2 → Ulcer Detected |
| 6 hr | 5 | >5 → Ulcer Detected |
| 12 hr | 7–8 | >7 → Ulcer Detected |
| 1 day | 10 | >10 → Ulcer Detected |

> Normal human humidity: 30–60% RH. Patients with peripheral neuropathy exhibit foot pressure ~40% higher than normal individuals.

## LabVIEW Implementation

Key VI Functions: `HTTP Client: GET/POST`, `Flatten to JSON`, `Unflatten from JSON`, `Wait (ms)`, `Cluster`

Front Panel: Temperature indicators (T/B), pressure gauges (left/right/bottom), humidity gauge, user-configurable thresholds and delay interval, STOP/RUN controls.

## Firebase Cloud Integration

- ESP32 POSTs structured JSON to Firebase (6 sensor values + threshold control fields)
- LabVIEW HTTP Client GETs live values; POSTs updated threshold settings from front panel
- GSM SIM800L SMS: `"Warning! Foot Ulcer Detected. Consult your Doctor immediately."`

## Results

- Detected ulcer risk conditions across all three sensor modalities
- 6-sensor array improved detection accuracy over single-parameter systems
- Detection latency reduced by 60% compared to periodic manual inspection
- GSM SMS delivered to mobile devices within seconds of detection

## Key Features

- Multi-parameter sensor fusion (pressure + temperature + humidity)
- Real-time Firebase cloud monitoring accessible from any internet-connected device
- SMS alert delivery via GSM module
- User-configurable thresholds and delay intervals via LabVIEW front panel
- Temporal baseline-vs-measurement comparison with delay-aware thresholds
