@echo off
title %~n0.py CLI

:loop
python "%~dp0\%~n0.py" %cmd%
echo.
set cmd=""
set /p cmd=%~n0.py 
goto loop