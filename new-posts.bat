@echo off
title %~n0.py CLI

:loop
echo.
set cmd=
set /p cmd=%~n0.py 
python "%~dp0\%~n0.py" %cmd%
goto loop