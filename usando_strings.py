import psycopg2
from datetime import timedelta, datetime
import time
import os

inicioDaExecucao = time.time()

CORES = ['ff00008b', 'ff2222b2', 'ff0000ff', 'ff4763ff', 'ff507fff', 'ff7aa0ff',
    'ff13458b', 'ff0b86b8', 'ff20a5da', 'ff60a4f4', 'ff87b8de', 'ffb3def5',
    'ffe16941', 'ffffbf00', 'ffffff00', 'ffd1ce00', 'ffd0e040', 'ffd4ff7f',
    'ff008000', 'ff32cd32', 'ff2fffad', 'ff9afa00', 'ff7fff00', 'ff90ee90', 'ff98fb98']
DATA_ATUAL = datetime.utcnow()
DATA_INICIAL = DATA_ATUAL - timedelta(days=1)
NOME_ARQUIVO_KML = os.getcwd() + r"\kml\focos_GO-24h.kml"
# Lista de CORES para pintar os ícones no Style

def inicializarBanco():
    # Conexão com o banco de dados
    try:
        conexaodb = psycopg2.connect(
            database='DATABASE',
            user='QUEIMADAS',
            password='PASSWORD',
            host='HOST',
            port="PORT"
        )
        print("Conexao com o banco bem sucedida!")
        return conexaodb.cursor()
    except psycopg2.DatabaseError as erro:
        print(f"Erro ao se conectar: {erro}")

def consultarBanco(cursor, sql):
    cursor.execute(sql)
    return cursor.fetchall()

def encerrarBanco(db):
    return db.close() 

with open(NOME_ARQUIVO_KML, "w+") as kml_file:
    # Cria lista de datas para serem usadas como id no Style
    horarios = []
    for i in range(0,25):
        horarios.append((DATA_ATUAL - timedelta(hours=i)).strftime("%Y-%m-%d %H"))

    # Cabeçalho base
    cabecalho = '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://earth.google.com/kml/2.1">\n<Document>\n<name>Monitoramento de Queimadas</name>\n<description>Monitoramento de queimadas em tempo Real.</description>\n'

    # Cria 25 styles para classificar o quão recente é um foco (0h-24h)
    for i in range (0, 25):
        style = f'<Style id="{horarios[i]}"><IconStyle><color>{CORES[i]}</color><scale>0.8</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_square.png</href></Icon></IconStyle><LabelStyle><scale>0.0</scale></LabelStyle><ListStyle></ListStyle></Style>\n'
        cabecalho += style
    cabecalho += '<Folder>\n<name>Focos por Satelite</name>\n'
    kml_file.writelines(cabecalho)
    
    db = inicializarBanco()
    # Consulta para pegar o dia atual e o dia anterior
    datas = consultarBanco(db, f"select distinct(data_pas)::date as data_pas from focos_operacao where data_pas::date>='{DATA_INICIAL}' order by 1;")
    
    # Laço para criar pastas e points com base no dia
    for data in datas:
        texto1 = f"<Folder>\n<name>{data[0]}</name>\n"
        kml_file.writelines(texto1)

        # Consulta os focos do dia (data[0])
        focos = consultarBanco(db, f"""
        select 
            to_char(f.latitude, '999D999999') as latitude, 
            to_char(f.longitude, '999D999999') as longitude, 
            f.cod_sat, 
            f.data_pas,
            f.name_1 as estado,
            f.name_2 as municipio
        from
            public.focos_operacao as f
        where
            f.data_pas::date ='{data[0]}'
            and f.data_pas >= '{DATA_INICIAL}'
            and id_0 = 33
            and id_1='52';
        """)

        for foco in focos:
            latitude = foco[0]
            longitude = foco[1]
            cod_sat = foco[2]
            data_pas = foco[3].strftime("%Y-%m-%d %H:%M:%S")
            estado = foco[4]
            municipio = foco[5]
            texto2 = f"<Placemark>\n<name>{data_pas}</name>\n<description><![CDATA[<br>LAT = {latitude}<br>LONG = {longitude}<br>DATA = {data_pas}<br>SATELITE = {cod_sat}<br>ESTADO = {estado}<br>MUNICÍPIO = {municipio}<br><br>]]></description>\n<styleUrl>#{data_pas[:-6]}</styleUrl>\n<Point>\n<coordinates>{longitude},{latitude}</coordinates>\n</Point>\n<LookAt>\n<longitude>{longitude}</longitude>\n<latitude>{latitude}</latitude>\n<range>5000</range>\n</LookAt>\n</Placemark>\n"
            kml_file.writelines(texto2)
            
        texto3 = "</Folder>\n"
        kml_file.writelines(texto3)

    texto4 = "</Folder>\n<ScreenOverlay>\n<name>Logo</name>\n<Icon>\n<href>http://queimadas.dgi.inpe.br/queimadas/portal-static/kml/images/logo.png</href>\n</Icon>\n<overlayXY x=\"1\" y=\"1\" xunits=\"fraction\" yunits=\"fration\"/>\n<screenXY x=\".96\" y=\".74\" xunits=\"fraction\" yunits=\"fraction\"/>\n<rotationXY x=\"0\" y=\"0\" xunits=\"fraction\" yunits=\"fraction\"/>\n<size x=\"0\" y=\"0\" xunits=\"fraction\" yunits=\"fraction\"/>\n<rotation>0</rotation>\n</ScreenOverlay>\n<ScreenOverlay>\n<name>Legendas</name>\n<Icon>\n<href>http://queimadas.dgi.inpe.br/queimadas/portal-static/kml/images/legend_hora.png</href>\n</Icon>\n<overlayXY x=\"1\" y=\"1\" xunits=\"fraction\" yunits=\"fraction\"/>\n<screenXY x=\".99\" y=\".74\" xunits=\"fraction\" yunits=\"fraction\"/>\n<rotationXY x=\"0\" y=\"0\" xunits=\"fraction\" yunits=\"fraction\"/>\n<size x=\"0\" y=\"0\" xunits=\"fraction\" yunits=\"fraction\"/>\n<rotation>0</rotation>\n</ScreenOverlay>\n</Document>\n</kml>"
    kml_file.writelines(texto4)

encerrarBanco(db)

fimDaExecucao = time.time()
print(f'Tempo de execucao de: {fimDaExecucao - inicioDaExecucao:.3f}s')
