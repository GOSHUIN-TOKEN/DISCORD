%~d0
cd %~d0%~p0

python -m pip install -U pip
python -m pip install discord==0.16.12

:LOOP_LABEL
python TempleBell.py
timeout 2
goto :LOOP_LABEL