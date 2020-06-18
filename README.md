Baixar última versão do:

- PADE em https://github.com/grei-ufc/pade
- generateDS em https://github.com/bressanmarcos/generateDS
- cimrdf.py em https://github.com/bressanmarcos/cimrdf.py
- mygrid em https://github.com/grei-ufc/MyGrid


## Ordem para implementação de Use Cases
(nomes dos objetos são provisórios e deverão ser atualizados)
Acompanhar UCs no Anexo A do TCC

- Comando de chaves 
ADC envia objeto ***SwitchingPlan*** para ACom
ACom interpreta o plano e ativa / desativa chaves na ordem indicada

- Diagnosticar falta
ACom envia ***Outage*** para ADC

- Corrigir descoordenação
ADC ***processa***
ADC gera objeto para Comando de Chaves

- Isolar trecho em falta
(mesmo de corrigir, outro objeto)

- Negociar

- Recompor

