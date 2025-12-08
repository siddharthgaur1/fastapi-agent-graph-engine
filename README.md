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


How To Run 
pip install -r requirements.txt
uvicorn app.main:app --reload
Open: http://127.0.0.1:8000/docs
