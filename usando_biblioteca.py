import simplekml
import psycopg2
import time
import os
from datetime import datetime, timedelta

class Ponto:
    def __init__(self, lat, lon, cod_sat, data, estado, municipio):
        self.data = data.strftime("%Y-%m-%d %H:%M:%S")
        self.latitude = lat
        self.longitude = lon
        self.satelite = cod_sat
        self.estado = estado
        self.municipio = municipio
        self.estilo = Estilo(self.data[:-6], CORES[horarios.index(self.data[:-6])])

    def criarPonto(self, pasta):
        ponto = pasta.newpoint(
            name=self.data,
            description=self.montarDescricao(),
            coords=[(self.longitude, self.latitude)]
        )
        ponto.lookat = simplekml.LookAt(
            longitude=self.longitude,
            latitude=self.latitude,
            range=5000
        )
        return self.estilo.aplicarEstilo(ponto)
    
    def montarDescricao(self):
        return f"LAT = {self.latitude}\nLONG = {self.longitude}\nDATA = {self.data}\nSATELITE = {self.data}\nESTADO = {self.estado}\nMUNICIPIO = {self.municipio}"

class Estilo:
    def __init__(self, id, cor):
        self.style = simplekml.Style()
        self.style._id = id
        self.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_square.png'
        self.style.iconstyle.color = cor
        self.style.iconstyle.scale = 0.8
        self.style.labelstyle.scale = 0

    def aplicarEstilo(self, ponto):
        ponto.style = self.style

class Database:
    def __init__(self):
        self.conexao = psycopg2.connect(
            database='DATABASE',
            user='USER',
            password='PASSWORD',
            host='HOST',
            port="PORT"
        )
        self.cursor = self.conexao.cursor()  

    def consultar(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def sair(self):
        self.conexao.close()

class Tela:
    def __init__(self, nome, documento):
        self.nome = nome
        self.documento = documento
        self.logo_url = "http://queimadas.dgi.inpe.br/queimadas/portal-static/kml/images/logo.png"
        self.legenda_url = "http://queimadas.dgi.inpe.br/queimadas/portal-static/kml/images/legend_hora.png"
        self.screen = self.documento.newscreenoverlay(name=self.nome)
        self.fraction = simplekml.Units.fraction
        self.screen.overlayxy = simplekml.OverlayXY(x=1, y=1, xunits=self.fraction, yunits=self.fraction)
        self.screen.size.x = 0
        self.screen.size.y = 0
        self.screen.size.xunits = self.fraction
        self.screen.size.yunits = self.fraction

    def montarLogo(self):
        self.screen.screenxy = simplekml.ScreenXY(x=.96, y=.84, xunits=self.fraction, yunits=self.fraction)        
        self.screen.icon.href = self.logo_url

    def montarLegenda(self):
        self.screen.screenxy = simplekml.ScreenXY(x=.99, y=.74, xunits=self.fraction, yunits=self.fraction)  
        self.screen.icon.href = self.legenda_url

tempoInicio = time.time()

NOME_ARQUIVO_KML = os.getcwd() + r"\kml\focos_GO-24h.kml"
DATA_ATUAL = datetime.utcnow()
DATA_INICIAL = DATA_ATUAL - timedelta(days=1)
CORES = ('ff00008b', 'ff2222b2', 'ff0000ff', 'ff4763ff', 'ff507fff', 'ff7aa0ff',
    'ff13458b', 'ff0b86b8', 'ff20a5da', 'ff60a4f4', 'ff87b8de', 'ffb3def5',
    'ffe16941', 'ffffbf00', 'ffffff00', 'ffd1ce00', 'ffd0e040', 'ffd4ff7f',
    'ff008000', 'ff32cd32', 'ff2fffad', 'ff9afa00', 'ff7fff00', 'ff90ee90', 'ff98fb98')

horarios = []
for i in range(25):
    horarios.append((DATA_ATUAL - timedelta(hours=i)).strftime("%Y-%m-%d %H"))

db = Database()
#datas = db.consultar(f"select distinct(data_pas)::date as data_pas from focos_operacao where data_pas::date>='{DATA_INICIAL}' order by 1;")

documento = simplekml.Kml(name="Monitoramento de Queimadas V2", description="Monitoramento de queimadas em tempo Real.")
mainFolder = documento.newfolder(name="Focos por Satélite")

datas = [DATA_INICIAL.strftime("%Y-%m-%d"), DATA_ATUAL.strftime("%Y-%m-%d")]
for data in datas:
    subFolder = mainFolder.newfolder(name=data)
    focos = db.consultar(f"""
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
            f.data_pas::date ='{data}'
            and f.data_pas >= '{DATA_INICIAL}'
            and id_0 = 33
            and id_1='52';
        """)
        
    for lat, lon, cod_sat, data_pas, estado, municipio in focos:
        ponto = Ponto(
            lat,
            lon,
            cod_sat,
            data_pas,
            estado,
            municipio
        ).criarPonto(subFolder) 

Tela("Logo", documento).montarLogo()
Tela("Legendas", documento).montarLegenda()

documento.save(NOME_ARQUIVO_KML)

tempoFim = time.time()
print(f'Tempo de execucao de: {tempoFim - tempoInicio:.3f}s')
