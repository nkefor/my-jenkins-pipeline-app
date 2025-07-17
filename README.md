# Compliance Tracker Application

This is a web application designed to help organizations track and manage their compliance with various regulations like GDPR, HIPAA, or PCI DSS. It provides a centralized system for managing compliance requirements, setting automated reminders, and integrating with cloud services for reporting.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup (Coming Soon)](#frontend-setup-coming-soon)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

*   **Compliance Checklist:** Define, track, and update compliance requirements, marking their status and adding notes.
*   **Automated Reminders:** Configure reminders for audits, policy reviews, or upcoming deadlines, delivered via email or in-app notifications.
*   **Cloud Reporting Integration:** Generate compliance reports based on checklist data, with options to integrate with cloud storage for easy sharing and archiving.

## Tech Stack

*   **Frontend:** Angular
*   **Backend:** Node.js (Express.js)
*   **Database:** MongoDB
*   **Authentication & Automation:** Firebase

## Project Structure

```
compliance-tracker/
├── backend/                  # Node.js Express.js Backend
│   ├── backend-server.js     # Main server file
│   ├── backend-package.json  # Backend dependencies
│   ├── .env.example          # Environment variables template
│   ├── firebase-admin-sdk.json # Firebase Service Account Key (PLACEHOLDER - DO NOT COMMIT)
│   └── ... (routes, models, controllers will be added here)
├── frontend/                 # Angular Frontend (Coming Soon)
│   └── ...
├── README.md                 # Project documentation
└── ...
```

## Getting Started

### Prerequisites

*   Node.js and npm installed
*   MongoDB installed and running
*   Firebase Project configured
*   Angular CLI installed (for frontend development)

### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd C:\Windows\System32 # Assuming you are in the root of the project
    ```
2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```
3.  **Configure Environment Variables:**
    *   Create a `.env` file in the `C:\Windows\System32` directory (same level as `backend-server.js`).
    *   Copy the contents of `.env.example` into your new `.env` file.
    *   **`MONGODB_URI`:** Update this with your MongoDB connection string (e.g., `mongodb://localhost:27017/compliance_tracker`).
    *   **Firebase Admin SDK:**
        *   Download your Firebase service account key JSON file from your Firebase project console (Project settings -> Service accounts -> Generate new private key).
        *   **Rename this downloaded JSON file to `firebase-admin-sdk.json`** and place it in the `C:\Windows\System32` directory.
        *   **IMPORTANT:** This file contains sensitive credentials. **DO NOT COMMIT `firebase-admin-sdk.json` or your `.env` file to version control.**

4.  **Start the Backend Server:**
    ```bash
    npm start
    # Or for development with auto-restarts:
    # npm run dev
    ```
    The backend API will be running on `http://localhost:3000` (or your specified PORT).

### Frontend Setup (Coming Soon)

Instructions for setting up the Angular frontend will be provided in a future update.

## Usage

Once both the backend and frontend are running, you will be able to:

*   Register and log in to the application.
*   Define and manage compliance checklists.
*   Set up reminders for compliance tasks.
*   Generate compliance reports.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests.

## License

This project is open-source and available under the [MIT License](LICENSE).