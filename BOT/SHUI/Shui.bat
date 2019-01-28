%~d0
cd %~d0%~p0

python -m pip install -U pip
python -m pip install -U discord.py
python -m pip install requests
python -m pip install require
python -m pip install emoji --upgrade

:LOOP_LABEL
python Shui.py
timeout 2
goto :LOOP_LABEL