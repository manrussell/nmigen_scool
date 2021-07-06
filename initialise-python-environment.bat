rem
rem batch script version
rem note i'm using python here not python3
rem
python -m venv scool
echo after running activate.bat you will have to run "pip3 install -r requirements.txt" manually
echo this seems to work in Ubuntu
scool\Scripts\activate.bat
rem call scool\Scripts\activate.bat
pip3 install -r requirements.txt
