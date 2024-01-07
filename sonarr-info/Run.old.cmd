set arg1=%1
set dir=%cd%
cd "%dir%" && %dir%\venv\Scripts\activate && pythonw %dir%\availability-labels.py %arg1% && %dir%\venv\Scripts\deactivate