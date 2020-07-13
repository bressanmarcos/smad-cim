REM cimrdf.py e generateDS devem estar instalados

REM DEFINIR CAMINHOS
set origin="..\artifacts"
set destination="..\information_model"

REM GERAR ESQUELETOS .PY PARA CADA .XSD -s "%destination%\%%~nisubs.py" --super="%super%.%%~ni" 
for /r %%i in "%origin%\*.xsd" do (
    echo "%%i --> %destination%\%%~ni.py"
    generateDS -o "%destination%\%%~ni.py" --export="write etree validate generator" --no-questions --silence "%%i"
)