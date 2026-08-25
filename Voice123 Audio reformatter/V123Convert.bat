@echo off
setlocal

REM Create the exported folder if it doesn't already exist
if not exist "exported" mkdir "exported"

REM Loop through all files in the imported folder
for %%f in ("imported\*.*") do (
    echo Processing: %%~nxf
    ffmpeg -i "%%f" -ac 1 -ar 44100 -acodec pcm_s16le -af "loudnorm=I=-16:TP=-3.0" "exported\%%~nf.wav"
)

echo.
echo All voiceover files have been formatted and moved to the exported folder!
pause