# AC Anomaly Detector (Eagle Vision)

## Domain
Edge AI | Computer Vision | Real-Time Surveillance Systems | Embedded AI

## Technologies
Python, OpenCV, YOLOv8n, Ultralytics, NVIDIA Jetson Nano 4GB, CUDA, Ubuntu 18.04, JetPack

## Concepts
Object Detection, Real-Time Inference, Edge AI Deployment, Threat Classification, Embedded Computer Vision, GPU Acceleration, Event Monitoring

## Detailed Work

- Built real-time anomaly detection system running entirely on NVIDIA Jetson Nano 4GB
- Implemented YOLOv8n-based object detection pipeline for live video analysis
- Designed configurable anomaly classification engine using custom threat class lists
- Engineered real-time threat detection workflows with confidence-based severity levels (HIGH ≥75%, MEDIUM 55–74%, LOW <55%)
- Optimized inference performance for embedded GPU hardware deployment
- Developed Eagle Vision inspired surveillance HUD using OpenCV
- Created custom visual overlay system with threat highlighting and tracking panels
- Implemented live event logging system with timestamped anomaly records
- Built flashing threat alert system for real-time anomaly notification
- Developed configurable camera pipeline supporting USB and CSI camera inputs
- Integrated FPS monitoring, session tracking, and object counting systems
- Designed modular architecture separating detection, overlays, and configuration management

## Hardware Stack

- NVIDIA Jetson Nano 4GB, USB Webcam / CSI Camera, Ubuntu 18.04 + JetPack, CUDA GPU acceleration

## Performance Metrics

- YOLOv8n inference: ~15–25 FPS on Jetson Nano 4GB
- 80 COCO detection classes, configurable anomaly trigger classes
- Real-time embedded GPU inference, local-first (no cloud dependency)

## Architecture Highlights

- Real-time camera ingestion pipeline
- YOLOv8n object detection engine
- Configurable anomaly classification layer with confidence-based severity scoring
- OpenCV Eagle Vision HUD renderer
- Event logging and monitoring system
- Modular configuration architecture
