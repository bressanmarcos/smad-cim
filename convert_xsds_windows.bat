REM DEFINIR AMBIENTE
set myenv=smad

REM MUDAR PARA AMBIENTE
call %activate% %myenv%

set activate="C:\Users\Bressan\Anaconda3\Scripts\activate.bat"
set generateds="..\python\generateDS\generateDS.py"

REM DEFINIR CAMINHOS
set origin=artifacts
set destination=information_modelgenerateDS -o "%destination%\%%~ni.py" --export="write etree validate generator" --no-questions --silence "%%i"

REM GERAR ESQUELETOS .PY PARA CADA .XSD -s "%destination%\%%~nisubs.py" --super="%super%.%%~ni" 
for /r %%i in "%origin%\*.xsd" do (
    echo "%%i --> %destination%\%%~ni.py"
    generateDS -o "%destination%\%%~ni.py" --export="write etree validate generator" --no-questions --silence "%%i"
)