## Ordem para implementação de Use Cases
(nomes dos objetos são provisórios e deverão ser atualizados)
***Acompanhar UCs no Anexo A do TCC***

- Comando de chaves (simples)
ACom interpreta o *SwitchingPlan* e ativa / desativa chaves na ordem indicada

- Diagnosticar falta
ACom envia ***Outage*** para ADC

- Corrigir descoordenação
ADC _processa_
ADC gera objeto *SwitchingPlan* para _Comando de Chaves_

- Isolar trecho em falta
(mesmo de *Corrigir*, outro objeto *SwitchingPlan*)

- Negociar
*SwitchingPlan*

- Recompor


