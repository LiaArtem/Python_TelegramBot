cd %cd%
PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& './telegrambot_build.ps1'"
PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& './telegrambot.ps1'"
pause