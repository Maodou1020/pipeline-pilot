PipelinePilot - COMP9001 Final Project
======================================

ENTRY POINT
-----------
Backend: backend/app.py
Frontend: frontend/src/main.js

PipelinePilot is a web-based visual CI/CD pipeline scheduler. It lets a user
create tasks, define dependencies, validate the resulting directed graph, and
simulate execution with a limited number of workers.

FULL PROJECT SOURCE
-------------------
https://github.com/Maodou1020/pipeline-pilot

The repository contains the Python backend, Vue frontend, requirements, and
setup instructions. Generated dependencies (node_modules and .venv) are not
part of the source submission; install them using the steps below.

IMPORTANT FOR MARKING
---------------------
This project is a web application and will not run inside the Ed Python
environment. It uses Python with Flask and SQLite for the main program, plus a
Vue 3 frontend. Please run it locally using the instructions below.

External Python libraries:
- Flask 3.1.2
- Flask-CORS 6.0.1

Frontend libraries/tools:
- Vue 3
- Vue Router
- Vite

RUN THE BACKEND
---------------
1. Open a terminal in the project folder.
2. Run:

   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   python app.py

The API will run at http://localhost:5001.

RUN THE FRONTEND
----------------
1. Open a second terminal in the project folder.
2. Run:

   cd frontend
   npm install
   npm run dev

3. Open http://localhost:5173 in a browser.

TEST LOGIN
----------
Username: Chris
Password: 123

RUN THE PYTHON TESTS
--------------------
From the backend directory with the virtual environment active:

   python -m unittest discover -s tests -v

The Python code demonstrates classes, validation, exception handling,
decorators, database persistence, graph traversal, cycle detection,
topological sorting, and an event-driven scheduling simulation.

The longer README.md contains the architecture, API summary, demo workflow,
configuration options, and security scope.
