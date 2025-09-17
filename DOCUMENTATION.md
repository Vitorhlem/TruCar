# TruCar Project Documentation

## 1. Project Overview

TruCar is a comprehensive fleet management platform designed to provide real-time tracking, optimize routes, reduce operational costs, and increase the efficiency of drivers and vehicles. The platform is suitable for various sectors, including agribusiness, freight, services, and civil construction.

## 2. Features

The TruCar platform offers a wide range of features to help you manage your fleet effectively:

*   **Smart Dashboard:** A centralized dashboard to visualize key performance indicators of your fleet.
*   **Travel Control:** Monitor and manage all your fleet's trips in real-time.
*   **Maintenance Management:** Schedule and track preventive and corrective maintenance for your vehicles.
*   **Fuel Control:** Monitor fuel consumption and identify opportunities for cost savings.
*   **Driver Ranking:** Rank your drivers based on their performance and driving behavior.
*   **Management Reports:** Generate detailed reports to support your decision-making process.
*   **Automatic Alerts:** Receive automatic alerts for important events, such as speeding or entering a restricted area.
*   **API for Integration:** Integrate TruCar with your existing systems using our powerful API.

## 3. Architecture

The TruCar project is composed of three main components: a frontend application, a backend server, and a vehicle simulator.

```
+-----------------+      +------------------+      +-----------------+
|                 |      |                  |      |                 |
|     Frontend    |----->|      Backend     |<-----|    Simulator    |
| (Quasar/Static) |      |    (FastAPI)     |      |    (Python)     |
|                 |      |                  |      |                 |
+-----------------+      +------------------+      +-----------------+
```

*   **Frontend:** The frontend is a web application that provides the user interface for the platform. It consists of a static landing page and potentially a Quasar application (as mentioned in `Readme.txt`). The landing page is built with HTML, CSS, and JavaScript.
*   **Backend:** The backend is a Python application built with the FastAPI framework. It exposes a REST API to be consumed by the frontend and the simulator. It is responsible for processing and storing telemetry data, as well as handling all the business logic of the platform.
*   **Simulator:** The simulator is a Python script that mimics a real vehicle by sending telemetry data to the backend API. This is useful for testing and development purposes.

## 4. Getting Started

This section provides instructions on how to set up and run the TruCar project on your local machine.

### 4.1. Prerequisites

*   Python 3.7+
*   pip
*   Node.js and npm (for the Quasar frontend)

### 4.2. Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Install the required Python packages. Note: `requirements.txt` is a Git LFS pointer, so you will need to infer the dependencies from the code or have Git LFS installed. A virtual environment is recommended.
    ```bash
    pip install fastapi uvicorn sqlalchemy alembic pydantic python-jose passlib bcrypt
    ```
3.  Run the database migrations:
    ```bash
    alembic upgrade head
    ```
4.  Start the backend server:
    ```bash
    python -m uvicorn main:app --reload
    ```
    The backend will be running at `http://127.0.0.1:8000`.

### 4.3. Frontend Setup

The project contains a static landing page and references a Quasar application.

*   **Static Landing Page:**
    To view the static landing page, simply open the `index.html` file in your web browser.

*   **Quasar Application:**
    The `Readme.txt` file provides the following instructions to run the Quasar application:
    1.  Navigate to the `FrontEnd` directory:
        ```bash
        cd FrontEnd
        ```
    2.  Install the dependencies:
        ```bash
        npm install
        ```
    3.  Start the development server:
        ```bash
        quasar dev
        ```

### 4.4. Simulator

1.  Open a new terminal and navigate to the root of the project.
2.  Run the simulator script:
    ```bash
    python simulator.py
    ```
    The simulator will start sending telemetry data to the backend.

## 5. API Documentation

The TruCar backend exposes a REST API for managing the platform. The base URL for the API is `http://127.0.0.1:8000/api/v1`.

### 5.1. Telemetry

This endpoint is used to report telemetry data from a vehicle.

*   **URL:** `/telemetry/report`
*   **Method:** `POST`
*   **Request Body:**

    The request body should be a JSON object with the following structure:

    ```json
    {
      "device_id": "string",
      "timestamp": "string (ISO 8601 format)",
      "latitude": "float",
      "longitude": "float",
      "engine_hours": "float"
    }
    ```

    **Example:**

    ```json
    {
      "device_id": "TRATOR-001",
      "timestamp": "2025-09-17T11:15:27.028450Z",
      "latitude": -23.5505,
      "longitude": -46.6333,
      "engine_hours": 1250.5
    }
    ```

*   **Response:**

    *   **204 No Content:** The telemetry data was received and processed successfully.
    *   **422 Unprocessable Entity:** The request body is invalid.
