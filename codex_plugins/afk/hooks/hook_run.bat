@echo off
chcp 65001>nul 2>&1

set "LOG_FILE=%cd%\.codex\logs\hooks.log"
set "EXECUTOR=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
set "EVENT_NAME=%~1"
set "EVENT_SCRIPT=%~dp0hook_on_%EVENT_NAME%.py"

goto :run

:write_log
set "LOG_DATE=%date%"
for /f "delims=0123456789" %%a in ("%LOG_DATE:~0,1%") do set "LOG_DATE=%LOG_DATE:* =%"
for /f "delims= " %%a in ("%LOG_DATE%") do set "LOG_DATE=%%a"
set "LOG_TIME=%time: =0%"
>> "%LOG_FILE%" echo [%LOG_DATE% %LOG_TIME%] %~1
exit /b 0

:run
if not exist "%LOG_FILE%" (
    for %%F in ("%LOG_FILE%") do mkdir "%%~dpF" 2>nul
    call :write_log "PLUGIN_ROOT=%PLUGIN_ROOT%"
    call :write_log "PLUGIN_DATA=%PLUGIN_DATA%"
    call :write_log "EXECUTOR=%EXECUTOR%"
)

call :write_log "execute %EVENT_SCRIPT%"
"%EXECUTOR%" "%EVENT_SCRIPT%" 2>> "%LOG_FILE%"
set "HOOK_EXIT_CODE=%ERRORLEVEL%"

if %HOOK_EXIT_CODE% neq 0 (
    call :write_log "hook failed with exit code %HOOK_EXIT_CODE%"
)

exit /b %HOOK_EXIT_CODE%
