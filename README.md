<h1 align="center">🧠 Minimal Agent Workflow Engine</h1>
<p align="center">FastAPI-based tool graph engine for stateful automation and AI workflows</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/REST%20API-000000?style=for-the-badge&logo=swagger&logoColor=white" />
  <img src="https://img.shields.io/badge/State%20Machine-5A5A5A?style=for-the-badge" />
</p>

This lightweight engine executes **agent-style workflows** as directed graphs of Python tools.  
It supports **state mutation, branching, looping, and execution logging**, making it suitable for AI pipelines, automation services, or custom agent architectures.

---

<img width="1620" height="639" alt="image" src="https://github.com/user-attachments/assets/9c2094b7-ca6d-4e2d-839c-5fe1e427f114" />
<img width="1284" height="416" alt="image" src="https://github.com/user-attachments/assets/db0db3fc-4f20-4d68-a731-5163b5b91ace" />


## ▶️ How To Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload

