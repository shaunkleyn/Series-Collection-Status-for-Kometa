set dir=%cd%
python -m venv venv && cd "%dir%" && %dir%\venv\Scripts\activate && pip install -r requirements.txt && %dir%\venv\Scripts\deactivate