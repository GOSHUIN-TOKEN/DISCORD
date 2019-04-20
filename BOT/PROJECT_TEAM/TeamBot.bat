%~d0
cd %~d0%~p0

python -m pip install -U pip
python -m pip install discord==0.16.12
python -m pip install requests

:LOOP_LABEL
python TeamBot.py
timeout 2
goto :LOOP_LABEL