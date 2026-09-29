# RecallMeet

### An AI agent that remembers every interaction and prepares you for what comes next.

RecallMeet is an AI-powered meeting memory assistant designed to retain important client interactions, recall relevant context, and prepare users for future meetings.

## 🔄 How It Works

RecallMeet follows a simple workflow:

**Retain → Recall → Prepare**

- **Retain** — Store important information from client meetings.
- **Recall** — Retrieve relevant information from previous interactions.
- **Prepare** — Turn previous context into useful preparation points for the next meeting.

## ✨ Features

- 📝 Remember important meeting information
- 🧠 Recall past client context
- 🎯 Prepare for upcoming meetings
- 📅 View meeting history
- 💰 Track project budgets
- 📅 Track timeline changes
- 🔐 Keep client context separated
- 🧠 Long-term AI memory using Hindsight

## 🛠️ Tech Stack

- **Python**
- **FastAPI**
- **HTML**
- **CSS**
- **JavaScript**
- **Hindsight** for long-term AI agent memory

## 🧩 Architecture

```text
Client Meeting
      ↓
   RETAIN
      ↓
Hindsight Memory
      ↓
    RECALL
      ↓
Relevant Client Context
      ↓
   PREPARE
      ↓
Next Meeting Brief
💡 Example
For a client such as TechNova Ltd, RecallMeet can remember:
Project budget: ₹8 lakh
Original timeline: 5 months
Security concern
Encryption and two-factor authentication requirements
When additional security work changes the delivery timeline to 6 months, RecallMeet can connect the new information with the previous meeting context.
The resulting meeting brief can highlight:
Previous commitments
Security requirements
Timeline changes
Unresolved concerns
Current budget
🧠 Why Hindsight?
RecallMeet uses Hindsight⁠� as its long-term memory layer.
Hindsight allows the application to retain information from previous interactions and recall relevant memories when they are needed.
Documentation: Hindsight Documentation⁠�
📁 Project Structure
RecallMeet/
│
├── backend.py
├── index.html
├── test_hindsight.py
└── README.md
⚙️ Running Locally
Install the required Python packages:
pip install hindsight-client python-dotenv fastapi uvicorn
Create a .env file containing your Hindsight configuration.
Never commit your .env file or API keys to GitHub.
Start the FastAPI backend:
uvicorn backend:app --reload
Then open:
http://127.0.0.1:8000
API documentation is available at:
http://127.0.0.1:8000/docs
🚧 Current Limitations
RecallMeet is currently a prototype. Future improvements could include:
Stronger authentication
More structured meeting extraction
Better memory management
Automatic follow-up detection
Commitment and deadline tracking
More advanced meeting preparation
👩‍💻 Project
Built as a practical exploration of long-term memory for AI agents.
RecallMeet — An AI agent that remembers every interaction and prepares you for what comes next.

