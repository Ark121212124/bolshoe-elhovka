QUICK START - FIXED WINDOWS LAUNCH

1) Unzip this archive to a simple path, for example:
   C:\diplom_appeals_crm

2) Open the project folder.

3) Double-click:
   start_project.bat

4) Wait until two black windows are opened:
   - Backend API CRM
   - Frontend Site

5) Open:
   Site: http://localhost:5500
   CRM:  http://localhost:8000/crm
   API:  http://localhost:8000/docs

6) CRM demo login:
   admin
   admin123

IMPORTANT:
- Do not run .env.example.
- Do not run requirements.txt.
- Do not move start_backend.bat into another folder.
- If Windows asks for permission, allow local network/private network.
- If port 8000 or 5500 is busy, close old cmd windows and run again.

If it still fails:
1) Open cmd in the project root folder.
2) Run:
   start_backend.bat
3) Send a screenshot of the first red error.
