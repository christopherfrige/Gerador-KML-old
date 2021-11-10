# Gerador-KML-old

**Há uma nova versão desse projeto, com diversas outras funcionalidades, [aqui](https://github.com/christopherfrige/Gerador-KML-Focos-Queimadas).**

Esse projeto teve como base um antigo código em PHP do **INPE**, que precisava ser transcrito para Python, que era usado para gerar arquivos de formato KML, formato suportado pelo Google Earth, de forma a visualizar os **focos de queimadas** no estado de Goiás. <br>
*Mais informações sobre o formato KML [aqui](https://developers.google.com/kml/documentation).*

## Versões

A primeira versão foi desenvolvida baseando-se na maneira que foi usada no gerador em PHP, trabalhando com *strings*. <br>

A segunda versão foi construída do zero, utilizando a biblioteca **SimpleKML**, feita com o fim de facilitar e otimizar a criação de KMLs. Como resultado do uso dela, além de uma maior organização do código, a performance melhorou em cerca de 20%.

## Requisitos

- **Python** com versão entre **3.6** e **3.9**
- Biblioteca **simplekml** ([documentação](https://simplekml.readthedocs.io/en/latest/))
- Biblioteca **psycopg2**,para acesso ao banco de dados. ([documentação](https://www.psycopg.org/docs/))

## Execução

Para execução desse projeto, o primeiro passo é criar um ambiente virtual (virtualenv), etapa descrita detalhadamente em outro projeto [aqui](https://github.com/christopherfrige/marketplaces-update-tracker#configurando-o-ambiente).

Após isso, para instalar as bibliotecas necessárias (simplekml e psycopg2), executar no terminal:

    pip install -r requirements.txt

Com tudo necessário instalado, alterar as credenciais de acesso ao banco de dados: <br>
![](https://i.imgur.com/A50V5F3.png)

Agora resta fazer a execução, em que o recomendado é a utilização da versão **V2**, do script **usando_biblioteca.py**:

    python usando_biblioteca.py
