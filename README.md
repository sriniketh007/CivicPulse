# CivicPulse 🏙️⚡

An AI-powered citizen governance and feedback platform designed to bridge the gap between citizens and city authorities through automated issue triage, real-time location tagging, and intelligent feedback analytics.

---

## 🌟 Key Features

- 👥 **Dual Role-Based Dashboards**:
  - **Citizen Portal**: Submit civic complaints, track issue status in real-time, and view local community updates.
  - **Authority Dashboard**: Manage complaints, track high-priority zones, and update issue statuses efficiently.
- 🤖 **Automated Gemini AI Classification**: Automatically parses, categorizes, and classifies incoming citizen feedback and severity levels using the Google Gemini API.
- 📱 **Secure Phone OTP Authentication**: Seamless and passwordless user authentication via phone-based OTP verification.
- 📍 **Location Tagging**: Precise geolocation tracking associated with submitted issues to aid municipal response teams.
- ⚡ **High-Performance Persistence**: Built using PostgreSQL and SQLModel for type-safe, high-speed database interactions.

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI
- **Database**: PostgreSQL, SQLModel ORM
- **AI / LLM Integration**: Google Gemini API
- **Authentication**: Phone-based OTP Service
- **Environment & Tools**: Python-dotenv, Uvicorn

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **PostgreSQL** installed and running locally or hosted on a cloud provider.
- A **Google Gemini API Key**.

### Installation & Local Setup

1. **Clone the Repository**:
   ```bash
   git clone [https://github.com/sriniketh007/CivicPulse.git](https://github.com/sriniketh007/CivicPulse.git)
   cd CivicPulse
