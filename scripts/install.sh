#!/bin/bash

# 安装系统依赖
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    python3-opencv \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    libhdf5-dev \
    libhdf5-serial-dev \
    libharfbuzz-dev \
    libwebp-dev \
    libjpeg-dev \
    libtiff5-dev \
    libopenjp2-7-dev \
    libilmbase-dev \
    libopenexr-dev \
    libgstreamer1.0-dev \
    python3-gst-1.0

# 安装Python依赖
pip3 install -r requirements.txt

# 创建必要的目录
mkdir -p data/faces
mkdir -p data/models
mkdir -p logs
mkdir -p config
