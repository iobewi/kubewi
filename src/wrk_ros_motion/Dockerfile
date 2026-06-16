ARG REGISTRY=registry.kubewi.internal:5000
FROM ${REGISTRY}/kubewi/ros-core:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-jazzy-control-msgs \
    ros-jazzy-controller-manager \
    ros-jazzy-ros2-control \
    ros-jazzy-ros2-controllers \
    && rm -rf /var/lib/apt/lists/*
