cd D:\Agent_Project
$env:PYTHONPATH = 'D:\Agent_Project\src;D:\Agent_Project'
.\\.venv\Scripts\python.exe -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
