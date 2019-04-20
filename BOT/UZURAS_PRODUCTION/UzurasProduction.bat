%~d0
cd %~d0%~p0

python -m pip install -U pip
python -m pip install discord==0.16.12
python -m pip install requests
python -m pip install Pillow


:LOOP_LABEL
python UzurasProduction.py
timeout 2
goto :LOOP_LABEL