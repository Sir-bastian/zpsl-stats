# ZPSL Stats Hub

A simple, centralized platform for Zimbabwe Premier Soccer League (ZPSL) statistics.

## 📌 The Problem
Currently, ZPSL match results and player stats are scattered across various social media pages, newspapers, and unofficial websites. This fragmentation makes it difficult for fans, journalists, and developers to find a single, reliable "source of truth" for league standings or player performance.

## 💡 The Solution
The **ZPSL Stats Hub** aims to solve this by gathering, organizing, and displaying league data in one accessible place. It transforms scattered information into a structured digital archive.

### Key Features (v1.0)
* **Live League Table:** A dynamic standings table that updates automatically as match results are recorded.
* **Match Results:** A comprehensive log of all scores from the 2026 season.
* **Top Scorers:** A "Golden Boot" leaderboard tracking the league's most clinical finishers.
* **Developer API:** A public gateway allowing other developers to pull ZPSL data into their own apps or websites.

## ⚙️ How It Works
1.  **Data Verification:** Match results and events (goals, cards, assists) are manually verified and entered through a secure Admin Dashboard to ensure high data quality.
2.  **Structured Storage:** All data is stored in a relational PostgreSQL database, linking players, teams, and matches accurately.
3.  **Universal Access:** Information is delivered via a mobile-friendly web interface and a structured REST API.



## 🛠 Built With
* **Backend:** [Django](https://www.djangoproject.com/) (Python Framework)
* **Database:** [PostgreSQL](https://www.postgresql.org/)
* **Frontend:** Planned migration to **React** or a similar modern framework for a dynamic user experience.
* **Deployment:** [Render](https://render.com/)
* **Development Philosophy:** This project is built using a "Human learning coding + AI" approach, leveraging AI tools to accelerate coding, debugging, and documentation.

## 📈 Project Status
**Current Phase:** Foundation (Weeks 1– n)
- [x] Database schema designed and implemented.
- [x] Secure Admin Dashboard setup for data entry.
- [ ] Public Standings & Results pages (In Progress).
- [ ] API Endpoints development (Upcoming).

> **Note:** This project is a work in progress. Deadlines and features may shift as the development process evolves and unforeseen challenges are addressed.