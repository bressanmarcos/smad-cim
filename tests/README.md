# Para realizar todos os testes

1) de dentro da pasta raiz do projeto:
```bash
python -m pytest
```
2) de dentro da pasta _tests_:
```bash
pytest
```
Os testes podem ser bastante demorados devido à necessidade de se ativar o PADE AMS em algum deles.

## Como funciona
O pytest é uma biblioteca que permite realizar testes de todos os tipos, possibilitando a injeção ou patching de comandos dentro das funçôes que estão sendo testadas.

Testes unitários são colocados na pasta _tests_, necessariamente em arquivos precedidos por _test\__ no nome do arquivo *python*.
Além disso, funções de teste devem ser igualmente precedidos por _test\__ para serem detectados, por exemplo:
```python
def test_validade():
    assert 1+1 == 2
```

Instruções de patch são identificadas pelo _decorator_ *@pytest.fixture*. Elas servem para realizar alguma modificação nas funções padrão implementadas no projeto com o propósito de manipular as condições de teste (printar algo na tela, impedir a chamada a uma função, modificar o comportamento de função ou método, modificar o PATH, inserir ou remover chaves de um _dict_, etc). No exemplo abaixo, _setattr_ é usada para su
```python
@pytest.fixture
def injetar_func(monkeypatch):
    def funcao_substituta(argumento1, argumento2, argumento3):
        ###
        return 
    monkeypatch.setattr({pacote ou pacote.classe}, {função ou método}, funcao_substituta)
```

Mais informações: https://docs.pytest.org/en/latest/