# Social Distancing Detector

## Domain
Edge AI | Computer Vision | Real-Time Surveillance Systems | Embedded AI

## Technologies
Python, OpenCV, NVIDIA Jetson Nano 4GB, TensorRT, jetson-inference, poseNet, Ubuntu 18.04, CUDA

## Concepts
Pose Estimation, Edge AI Inference, Euclidean Distance Computation, Multi-Person Tracking, Real-Time Video Processing, TensorRT Optimization

## Detailed Work

- Built real-time social distancing violation detection system on NVIDIA Jetson Nano 4GB
- Implemented multi-person pose estimation using poseNet from Dusty's jetson-inference framework
- Utilized TensorRT-accelerated inference (FP16) for optimized edge AI performance
- Designed human localization system using hip-center body keypoint calculations
- Implemented Euclidean distance computation between detected individuals
- Developed configurable violation threshold detection pipeline
- Engineered real-time visual alert system for unsafe distancing violations
- Created Eagle Vision themed surveillance HUD with flashing breach alerts
- Implemented dashed-line visual indicators between violating individuals
- Built real-time FPS monitoring and session tracking system
- Optimized embedded inference workflows for low-power edge hardware
- Developed modular architecture separating inference, overlays, and distance logic

## Hardware Stack

- NVIDIA Jetson Nano 4GB, Logitech C270 HD Webcam, Ubuntu 18.04 (JetPack), CUDA TensorRT FP16

## Performance Metrics

- poseNet resnet18-body inference: ~15–20 FPS on Jetson Nano 4GB
- TensorRT FP16 acceleration, configurable distance threshold, real-time multi-person analysis

## Architecture Highlights

- Camera ingestion pipeline
- poseNet TensorRT inference engine
- Human keypoint extraction → hip-center localization algorithm
- Euclidean distance analysis engine
- Real-time violation detection pipeline
- OpenCV HUD rendering system
- Event logging and monitoring layer
