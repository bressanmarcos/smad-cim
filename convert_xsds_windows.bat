REM DEFINIR AMBIENTE
set myenv=smad

REM DEFINIR CAMINHOS
set activate="C:\Users\Bressan\Anaconda3\Scripts\activate.bat"
set generateds="..\python\generateDS\generateDS.py"
set artifacts=(..\artifacts\*.xsd)
set destination=information_model
set super=information_model

REM MUDAR PARA AMBIENTE
call %activate% %myenv%

REM GERAR ESQUELETOS .PY PARA CADA .XSD -s "%destination%\%%~nisubs.py" --super="%super%.%%~ni" 
for /r %%i in %artifacts% do python %generateds% -o "%destination%\%%~ni.py" --export="write etree validate generator" --no-questions --silence "%%i"