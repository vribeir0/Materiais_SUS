from flask import Flask, redirect, request, render_template
from haversine import haversine
import csv
import psycopg2
import jinja2
import math

# variavel de inicio do app
app = Flask(__name__, template_folder='templates', static_url_path='/static')
app.secret_key = "secret"

def inicializar():
    try:
        
        # # conexão do banco
        # conn = psycopg2.connect(dbname='#####', user='#####',
        #                         password='#####', host='localhost', port=5435)
        # print("Conexão com banco de dados realizada com sucesso")
        # cur = conn.cursor()
        # #SELECT que realiza a obtenção dos dados da base e realiza a transformação das coordenadas em ESPG 28192(SAD69) para ESPG 4326
        # cur.execute("SELECT gid, pre_nome, nome, ST_X(ST_TRANSFORM(geom,'+proj=utm +zone=22 +south +ellps=aust_SA +units=m +no_defs' ,4326)) AS lon, ST_Y(ST_TRANSFORM(geom,'+proj=utm +zone=22 +south +ellps=aust_SA +units=m +no_defs' ,4326)) AS lat, alcool_gel_l, cnes  FROM saude.hospital_covid WHERE alcool_gel_l > -1 and coord_e is not NULL ORDER BY (pre_nome,nome)")
        # result = cur.fetchall()    
        # items = []
        # #iterando todos os selects dos hospitais e inserindo em um dict
        # for itr in result:
        #     item = dict(gid=itr[0], prenome=itr[1], nome=itr[2],
        #                 lat=itr[4], lon=itr[3], alcool=itr[5], 
        #                 cnes=itr[6])
        items = []

        reader = csv.DictReader(open(".\static\csv\coordenadas.csv"))
        for item in reader:
            items.append(item)
        return items
    except:
        return -1
#função que realiza o cauculo da distancia entre os dois pontos
def distance_km(x1, y1, x2, y2):
    x1 = float(x1)
    y1 = float(y1)
    x2 = float(x2)
    y2 = float(y2)
    coord1 = (x1 , y1)
    coord2 = (x2, y2)
    proximo = haversine(coord1, coord2)
    return proximo
# inicializar rotas
# ---Rota principal, gerar HTML, preencher o mapa com pontos padrão antes da interação do usuário
@app.route("/")
@app.route("/index")
def index():
    print("Servidor Inicializado")
    try:
        items = inicializar()
            # condicional para renderização de página de erro 
            # if items == -1:
            #     var = "Conexão indisponível. Código de erro"
            #     print(var)
            #     print(e)
            #     return render_template('erro.html')
            # else:
        return render_template('index.html', items=items)
    #caso ocorra algum erro no carregamento do site ou conexão com o banco.
    except:
        return render_template('erro.html')


@app.route("/consulta/", methods=['POST'])
def consulta():
    # consultar banco e csv para formar lista
    items = inicializar()
    # OBTER latide Longitude DO GID ENVIADO
    gid = int(request.form.to_dict()['gid'])
    # gid-type integer
    lat_or = 0
    lon_or = 0
    for data in items:
        if int(data['gid']) == gid:
            lat_or = data['lat']
            float(lat_or)
            lon_or = data['lon']
            float(lon_or)
            break
    # CALCULAR MENOR
    # valor absurdo
    distancia_menor = 1800000
    gid_menor = -1
    lat_menor = -1
    lon_menor = -1
    nome_menor = -1
    prenome_menor = -1
    alcool_menor = -1
    cnes_menor = -1
    for data in items:
        distancia_menor_suposta = distance_km(lat_or, lon_or, data['lat'], data['lon'])
        #variais de controle para todos os campos do dict.
        gid_atual = int(data['gid'])
        lat_atual = data['lat']
        lon_atual = data['lon']
        prenome_atual = data['prenome']
        nome_atual = data['nome']
        alcool_atual = data['alcool']
        cnes_atual = data['cnes']
        #testes para descobrir qual é o hospital mais próximo e armazenar todos seus campos
        if lat_atual != "None":
            if ((gid_atual != gid) and (distancia_menor_suposta < distancia_menor)):
                distancia_menor = distancia_menor_suposta
                gid_menor = gid_atual
                lat_menor = lat_atual
                lon_menor = lon_atual
                prenome_menor = prenome_atual
                nome_menor = nome_atual
                alcool_menor = alcool_atual
                cnes_menor = cnes_atual
    #retorno do dict em forma de JSON para o javascript
    return {'hospital_proximo': [gid_menor, prenome_menor, nome_menor, lat_menor, lon_menor, distancia_menor, alcool_menor, cnes_menor]}
# definições da aplicação, endereço e porta de hospedagem
if __name__ == "__main__":
    app.run(port=7520, debug=False)
