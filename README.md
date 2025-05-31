# Virtual HealthCare Assistant

This repository contains the code to run an AI-powered assistant to provide medical advice, answer patient queries, and triage symptoms, enhancing patient engagement and care.

Porblem statement domain: Healthcare

## Preview
Live: https://medibuddyai.streamlit.app/

## Overview

The project focuses on providing patients with medical education, answering patient queries, and triaging symptoms, enhancing patient engagement with care using a virtual assistant.

## Project Structure

The project is structured as follows:

- `virtual_doc.py`: Application to run the virtual assistant.
- `Dockerfile`: Docker configuration for containerizing the application.
- `requirements.txt`: File containing the necessary dependencies to run the project.

## Tech Stacks
- LLMs: xAI-Grok-3-latest and Nvidia Palmyra-med-32B models.
- Platform: Streamlit.
- Deployment: Containerized (Docker) and Streamlit Community Cloud.
- Additional features: Voice interaction, PDF report generation, MCP Protocol.

## Getting Started

To get started with the project, follow these steps:

1. Clone this repository to your local machine.
    ```bash
    git clone https://github.com/RiteshYennuwar/Virtual_HealthCare_Assistant.git
    cd MediBuddyAI
2. Install the required dependencies using 
    ```bash
    pip install -r requirements.txt

## Usage

- **Application**:  To start the application and use the virtual assistant, execute the following command:
    ```bash
    streamlit run virtual_doc.py

After running the command, navigate to http://localhost:8501/ in your web browser to access the application.

## Docker Setup

To containerize the application and run it using Docker, follow these steps:

1. Build the Docker image:
    ```sh
    docker build -t virtual_doc-app .
    ```
2. Run the Docker container:
    ```sh
    docker run -p 8051:8051 virtual_doc-app
    ```
3. Access the web interface at http://localhost:8501/.

