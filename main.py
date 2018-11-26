from flask import Flask, jsonify, render_template, request
from flask import jsonify
from py2neo import Graph, Node, Relationship, Database, NodeMatcher
import json

app = Flask(__name__)


@app.route('/')
def index():
    # Conectamos con la BBDD NEO4j
    graph = Graph("http://neo4j:neo4j@localhost:7474/db/data/")

    # LANZAMOS LAS QUERIES PARA CALCULAR LOS ALGORITMOS
    # PageRank
    graph.run('''CALL algo.pageRank(
        'MATCH (n) RETURN id(n) AS id',
        'MATCH (n)-->(m) RETURN id(n) AS source, id(m) AS target',
        {graph: "cypher", iterations:5, writeProperty:'pagerank'})''')

    # Closenness - Harmonic Centrality
    graph.run('''CALL algo.closeness.harmonic(
      'MATCH (n) RETURN id(n) as id',
      'MATCH (n)-->(m) RETURN id(n) as source, id(m) as target',
      {graph:'cypher', writeProperty: 'centrality'})''')

    # Betweenness Centrality
    graph.run('''CALL algo.betweenness(null,null,
        {direction:'both',write:true, writeProperty:'betweenness'})
        YIELD nodes, minCentrality, maxCentrality, sumCentrality, loadMillis, computeMillis, writeMillis;''')

    # Louvain
    graph.run('''CALL algo.louvain(
      'MATCH (n) RETURN id(n) as id',
      'MATCH (n)-->(m) RETURN id(n) as source, id(m) as target',
      {graph:'cypher',writeProperty:'louvain'})''')

    # Componentes Conexas | Property: partition
    graph.run('''CALL algo.unionFind(
      'MATCH (n) RETURN id(n) as id',
      'MATCH (n)-[r]->(m) RETURN id(n) as source, id(m) as target, r.weight as weight',
      {graph:'cypher',write:true})''')
    #
    # return render_template('index.html')
# @app.route('/datos', methods=['GET', 'POST'])
# def datos():

    # Conectamos con la BBDD NEO4j
    # graph = Graph("http://neo4j:neo4j@localhost:7474/db/data/")

    # Cremos listas para guardar los datos que extraigamos de la BBDD
    nodes = []
    links =[]
    pagerank = []
    top_followers=[]
    conexas = []
    closenness=[]
    louvain=[]
    betwenneess = []

    # Query para sacar de NEO4j los nodos con las caracteristicas que vemos a usar en la APP
    queryNodes = graph.run('''MATCH (n)
    RETURN n.userID AS userID, n.name AS name, n.screen_name AS screen_name, n.verified AS verified,
    n.num_friends AS num_friends, n.num_status AS num_status, n.num_followers AS num_followers,
    n.image AS image, n.type AS type, id(n) AS id, n.pagerank AS pagerank, n.partition AS partition, n.betweenness AS betweenness,
    n.centrality AS centrality, n.louvain AS louvain''').data()

    for q in queryNodes:
        nodes.append(q)

    # Query para sacar los links con las caracteristics (source y target) que necesitamos para la vizualizacion
    queryLinks  = graph.run('MATCH (n) -->(m) RETURN id(n) AS source, id(m) AS target').data()
    links_list = queryLinks

    # Sacamos el TOP de los usuarios que tienen mas NUMERO DE SEGUIDORES y los guardamos en un JSON
    top_follow = graph.run(
        '''MATCH (n) WHERE EXISTS(n.num_followers) RETURN n.name AS Nombre,
        n.type AS Tipo_Usuario,
        n.num_followers AS Num_Seguidores ORDER BY Num_Seguidores DESC LIMIT 5''').data()
    for top in top_follow:
        top_followers.append(top)
    with open("static/data/top_followers.json", 'w+') as n:
        json.dump(top_followers, n)

    top_page = graph.run(
        '''MATCH (n) WHERE EXISTS(n.pagerank) RETURN n.name AS Nombre, n.type AS Tipo_Usuario,
        n.pagerank AS PageRank ORDER BY PageRank DESC LIMIT 5''').data()
    for t in top_page:
        pagerank.append(t)
    with open("static/data/top_pagerank.json", 'w+') as m:
        json.dump(pagerank, m)

    # Top CLOSENNESS HARMONIC
    top_closenness = graph.run(
            '''MATCH (n) WHERE EXISTS(n.centrality) RETURN DISTINCT n.name  as Nombre,
            n.type as Tipo_Usuario,
            n.centrality AS Closenness ORDER BY Closenness DESC LIMIT 5''').data()
    for h in top_closenness:
        closenness.append(h)
    with open("static/data/top_closenness.json", 'w+') as ha:
            json.dump(closenness, ha)

    # Top BETWEENNESS
    top_betweenness = graph.run('''
    MATCH (n) WHERE EXISTS(n.betweenness) RETURN DISTINCT n.name AS Nombre,
    n.type AS Tipo_Usuario, n.betweenness AS Betweenness ORDER BY Betweenness DESC LIMIT 5''').data()
    for b in top_betweenness:
        betwenneess.append(b)
    with open("static/data/top_betweenness.json", "w+") as be:
        json.dump(betwenneess, be)

    # # Aqui no podemos sacar el TOP 5 de usuarios , sino que sacamos el las comunidades que hay y el tamanno de cada una
    # TOP COMUNIDADES

    # Top COMPONENTES CONEXAS
    top_conexas = graph.run(
        '''MATCH (n)
    RETURN distinct (n.partition) as Componentes_Conexas,
    count(n) as Cantidad_nodos ORDER by Cantidad_nodos DESC''').data()
    for p in top_conexas:
        conexas.append(p)
    with open("static/data/top_conexas.json", 'w+') as o:
        json.dump(conexas, o)

     #Top LOUVAIN
    top_louvain = graph.run(
        '''MATCH (n)
        RETURN distinct (n.louvain) as Comunidades_Louvain,
        count(n) as Cantidad_nodos ORDER by Cantidad_nodos DESC''').data()
    for l in top_louvain:
        louvain.append(l)
    with open("static/data/top_louvain.json", 'w+') as lo:
        json.dump(louvain, lo)

    # Guardamos los datos que hemos sacado de NEO4j en un JSON para visualizarlo en la APP
    with open("static/data/datos.json", 'w+') as f:
        links1= links_list[0:]
        a = {"nodes": nodes, "links":links1}
        json.dump(a, f)
        # return jsonify(a)

    return render_template('index.html')
@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template('main/main.html')


# Visualizacion por defecto segun el NUMERO DE SEGUIDORES
@app.route('/graph', methods=['GET', 'POST'])
def graph():
    return render_template('grafo.html')

# Visualizacion PAGERANK
@app.route('/pageRank', methods=['GET','POST'])
def pageRank():
    return render_template('pagerank.html')

# Visualizacion CLOSENNESSS HARMONIC
@app.route('/closenness', methods=['GET','POST'])
def closenness():
    return render_template('closenness.html')

# Visualizar BETWEENNESS Centrality
@app.route('/betweenness', methods=['GET','POST'])
def betweenness():
    return render_template('betweenness.html')

#Visualizacion del ALGORTIMO DE COMUNIDADES LOUVAIN
@app.route('/louvain', methods=['GET','POST'])
def louvain():
    return render_template('louvain.html')

# TODO Calcular y Visualizar LABEL PROPAGATION
# @app.route('/graph/labelPropagation', methods=['GET','POST'])
# def labelPropagation():
#     return render_template('visualizacion_base.html')
#
#Visualizacion del ALGORTIMO DE COMUNIDADES COMPONENTES CONEXAS
@app.route('/componentesConexas', methods=['GET','POST'])
def connectedComponents():
    return render_template('componentesConexas.html')


if __name__=='__main__':
    app.run(debug=True)