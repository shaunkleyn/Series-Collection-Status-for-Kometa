@Echo Off
setlocal enabledelayedexpansion

for %%I in (.) do set dirname=%%~nxI

set arg1=%1
set venvpath=C:\venv\%dirname%
Set "VIRTUAL_ENV=%venvpath%"

If Not Exist "%VIRTUAL_ENV%\Scripts\activate.bat" (
    echo Creating virtual environment
    pip.exe install virtualenv
    python.exe -m venv %VIRTUAL_ENV%
) else (
    Echo Virtual environment already exists
)

If Not Exist "%VIRTUAL_ENV%\Scripts\activate.bat" (
    Echo Activation script does not exist.  Unable to continue.
    Exit /B 1
)

Call "%VIRTUAL_ENV%\Scripts\activate.bat"

IF Exist "requirements.txt" (
    Echo Checking required packages...
    @echo off
    pip.exe install -r requirements.txt | findstr /V /C:"Requirement already satisfied"
)


for %%A in (*.py) do (
    cls
    color 07
    set "file=%%~nA.py"
    echo Using !file!
    if exist !file! (
        Echo Executing '!file!' script...
        python !file! !arg1!
        deactivate
    )
)

:: Check the error level
if %ERRORLEVEL% NEQ 0 (
	%VIRTUAL_ENV%\Scripts\deactivate
    echo An error occurred! Error level: %ERRORLEVEL%
    :: Add your actions or commands to execute on error here
    :: For example, you can exit the script with an error code
    exit /b 1
) else (
    echo The command executed successfully.
	%VIRTUAL_ENV%\Scripts\deactivate
    :: Add your actions or commands for successful execution here
)
endlocal

:: The code below will run when Ctrl+C is pressed.
echo Ctrl+C was pressed! Executing interrupt actions...
%VIRTUAL_ENV%\Scripts\deactivate
:: Add your actions or commands to execute here
:: For example, you can exit the script
Exit /B 0