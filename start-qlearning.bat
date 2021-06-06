@echo off
cd %cd%
IF EXIST qlearningEnv\ GOTO START

:instalar
echo INSTALANDO DEPENDENCIAS

	

pip install virtualenv

virtualenv qlearningEnv
call .\qlearningEnv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r .\source\requirements.txt


:START
call .\qlearningEnv\Scripts\activate.bat
cd source
start python main.py
EXIT
