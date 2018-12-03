%~d0
cd %~d0%~p0

python -m pip install -U pip
python -m pip install -U discord.py

:LOOP_LABEL
python TempleBell.py
timeout 2
goto :LOOP_LABEL