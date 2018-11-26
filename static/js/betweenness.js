
// VISUALIZACION PARA EL ALGORTIMO DE BETWEENNESS

var datosTotales = {};

// Funcion que filtra los links que afectan a una lista de nodos
// No se tienen en cuenta las aristas si el origen o el destino no se van a pintar
function calcularAristas(nodos) {
    var aristas = [];
    datosTotales.links.forEach(function (e) {
        var origen = nodos.filter(function (n) {
            return n.id === e.source;
        })[0];

        var destino = nodos.filter(function (n) {
            return n.id === e.target;
        })[0];

        if (origen && destino) {
            aristas.push({
                source: origen,
                target: destino
            });
        }
    });

    return aristas;
}

// Funcion para que los nodos no se solapen
function collide(alpha, node) {
   var padding = 5;
   var maxRadius = 10;
    var quadtree = d3.geom.quadtree(node);
    return function(d) {
        var r = d.radius + maxRadius + padding,
                nx1 = d.x - r,
                nx2 = d.x + r,
                ny1 = d.y - r,
                ny2 = d.y + r;
        quadtree.visit(function(quad, x1, y1, x2, y2) {
            if (quad.point && (quad.point !== d)) {
                var x = d.x - quad.point.x,
                        y = d.y - quad.point.y,
                        l = Math.sqrt(x * x + y * y),
                        r = d.radius + quad.point.radius + padding;
                if (l < r) {
                    l = (l - r) / l * alpha;
                    d.x -= x *= l;
                    d.y -= y *= l;
                    quad.point.x += x;
                    quad.point.y += y;
                }
            }
            return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
        });
    };
};

// Funcion principal que pinta el grafo
function pintarGrafo(tipoGrafo, nodos) {
    console.log(nodos);
    // Parametros del grafo
    var width = 1840;
    // var width = 1286;
    // var height = 584;
    var height = 900;

    // Calculamos las aristas que afectan a los nodos
    var aristas = calcularAristas(nodos);


    // Tooltips
    var tip = d3.tip()
        .attr('class', 'd3-tip')
        .offset([-10, 0])
        .html(function (d) {
            switch (d['type']) {
                case 'Usuario':
                    return "<strong>Usuario</strong>" +
                        "<br>" +
                        "<strong> Nombre: " + d['name'] + "</strong>" +
                        "<br>" +
                        "<strong>Nº Seguidores: " + d['num_followers'] + "</strong>" +
                        "<br>" +
                        "<strong>Nº Amigos: " + d['num_friends'] + "</strong>"
                         + "<br>"+
                        "<strong>Valor Betweenness: "+ d['betweenness'] +"</strong>";
                case 'Mencionado':
                    return "<strong> Usuario Mencionado </strong>" +
                        "<br>" +
                        "<strong> Nombre: " + d['name'] + "</strong>" +
                        "<br>" +
                        "<strong>Nº Seguidores: " + d['num_followers'] + "</strong>" +
                        "<br>" +
                        "<strong>Nº Amigos: " + d['num_friends'] + "</strong>"
                        + "<br>"+
                        "<strong>Valor Betweenness: "+ d['betweenness'] +"</strong>";
                case 'Respondido':
                    return "<strong> Usuario Respondido </strong>" +
                        "<br>" +
                        "<strong> Nombre: " + d['name'] + "</strong>" +
                        "<br>" +
                        "<strong> Nº Seguidores: " + d['num_followers'] + "</strong>" +
                        "<br>" +
                        "<strong>Nº Amigos: " + d['num_friends'] + "</strong>"
                        + "<br>"+
                        "<strong>Valor Betweenness: "+ d['betweenness'] +"</strong>";
                case 'Retuiteado':
                    return "<strong> Usuario Retuiteado </strong>" +
                        "<br>" +
                        "<strong> Nombre: " + d['name'] + "</strong>" +
                        "<br>" +
                        "<strong>Nº Seguidores: " + d['num_followers'] + "</strong>" +
                        "<br>" +
                        "<strong>Nº Amigos: " + d['num_friends'] + "</strong>"
                        + "<br>"+
                        "<strong>Valor Betweenness: "+ d['betweenness'] +"</strong>";
                case 'Retuiteador':
                    return "<strong> Usuario que Retuitea </strong>" +
                        "<br>" +
                        "<strong> Nombre: " + d['name'] + "</strong>" +
                        "<br>" +
                        "<strong>Nº Seguidores: " + d['num_followers'] + "</strong>" +
                        "<br>" +
                        "<strong>Nº Amigos: " + d['num_friends'] + "</strong>"
                        + "<br>"+
                       "<strong>Valor Betweenness: "+ d['betweenness'] +"</strong>";
                case 'Citado':
                    return "<strong> Usuario Citado</strong>" +
                        "<br>" +
                        "<strong> Nombre: " + d['name'] + "</strong>" +
                        "<br>" +
                        "<strong>Nº Seguidores: " + d['num_followers'] + "</strong>" +
                        "<br>" +
                        "<strong>Nº Amigos: " + d['num_friends'] + "</strong>"
                        + "<br>"+
                        "<strong>Valor Betweenness: "+ d['betweenness'] +"</strong>";
                default:
                    return "<strong> Nombre: " + d['name'] + "</strong>";
            }
        });

    // Borramos el contenido anterior
    $('#grafo').empty();

    // Utilizamos el tipo de grafo 'force' de d3.js
    var force = d3.layout.force()
        .gravity(0.3)
        .distance(200)
        .charge(-120)
        .size([width, height]);

    // Creamos el svg
    var svg = d3.select('#grafo').append("svg")
        .attr("width", width)
        .attr("height", height);

    // Añadimos la estructura defs, donde se guardara la informacion de las imagenes
    var pattern_def = svg.append("defs");

    // Añadimos los tooltips
    svg.call(tip);

    // Aristas
    var link = svg.selectAll(".link")
        .data(aristas)
        .enter().append("line")
        .attr("class", "link")
        .style("stroke-width", 1);

    // Nodos
    var node = svg.selectAll(".node")
        .data(nodos)
        .enter().append("circle")
        .style("stroke-width", 5)
        .attr("class", "node")
        //Tamaño del nodo en funcion del Pagerank
        .attr("r", function (d) {
            if (d['betweenness'] >= 1000) {
                return 14 + (0.005 * d['betweenness'] / 100);
            }
            else if (d['betweenness'] >= 100) {
                return 12 + (0.5 * d['betweenness'] / 100);
            }
            else if (d['betweenness'] >= 50) {
                return 10+ (d['betweenness'] / 100);
            }
            else if (d['betweenness'] >= 10) {
                return 5+ (d['betweenness'] / 100);
            }
            else if (d['betweenness'] == 0) {
                return 2;
            }
            // else {
            //     return 8 + (0.1 * d['betweenness'] / 100);
            // }
        })
        .call(force.drag)
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide)
        .on('dblclick', connectedNodes)
        .each(function (d, i) {
            if ('image' in d) {
                pattern_def.append("pattern")
                    .attr("id", "node-img" + i)
                    .attr("patternUnits", "objectBoundingBox")
                    .attr({
                        "width": "100%",
                        "height": "100%"
                    })
                    .attr({
                        "viewBox": "0 0 1 1"
                    })
                    .append("image")
                    .attr("link:href", d['image'])
                    .attr({
                        "x": 0,
                        "y": 0,
                        "width": "1",
                        "height": "1",
                        "preserveAspectRatio": "none"
                    });
                d3.select(this).attr("fill", "url(#node-img" + i + ")")
            }
            else{
                node.attr("fill", function (d) {
                    switch (d['type']) {
                        case "Usuario":
                            return '#eff70e';
                        case 'Mencionado':
                            return '#02c38a';
                        case 'Respondido':
                            return '#ca7ff9';
                        case 'Retuiteado':
                            return '#f97f95';
                        case 'Retuiteador':
                            return '#0b7982';
                        case 'Citado':
                            return '#efb353';
                        default:
                            return '#050505';
                    }
                })
            }
        })
        //Color borde
        .style("stroke", function(d) {
            switch (d['type']) {
                case "Usuario":
                    return '#eff70e';
                case 'Mencionado':
                    return '#02c38a';
                case 'Respondido':
                    return '#ca7ff9';
                case 'Retuiteado':
                    return '#f97f95';
                case 'Retuiteador':
                    return '#0b7982';
                case 'Citado':
                    return '#efb353';
                default:
                    return '#050505';
            }
        });

    force
        .links(aristas)
        .nodes(nodos)
        .start();

    node.select("circle").forEach(collide(.20, node));

    force
        .on("tick", function () {
            link.attr("x1", function (d) {
                    return d.source.x;
                })
                .attr("y1", function (d) {
                    return d.source.y;
                })
                .attr("x2", function (d) {
                    return d.target.x;
                })
                .attr("y2", function (d) {
                    return d.target.y;
                });

            node.attr("cx", function (d) {
                    return d.x;
                })
                .attr("cy", function (d) {
                    return d.y;
                });
        });

        // Variable para ver si esta marcado o no
        var toggle = 0;

        //Array guardamos lo que esta conectado por el indice
        var linkedByIndex = {};
        for (var i = 0; i < datosTotales.nodes.length; i++) {
            linkedByIndex[i + "," + i] = 1;
        };
        aristas.forEach(function (d) {
            linkedByIndex[d.source.index + "," + d.target.index] = 1;
        });

        function neighboring(a, b) {
            return linkedByIndex[a.index + "," + b.index];
        }

         // Funcion que resalta los nodos si son vecinos
        function connectedNodes() {
            if (toggle == 0) {
                d = d3.select(this).node().__data__;
                node.style("opacity", function (o) {
                    return neighboring(d, o) | neighboring(o, d) ? 1 : 0.1;
                });

                link.style("opacity", function (o) {
                    return d.index == o.source.index | d.index == o.target.index ? 1 : 0.1;
                });

                toggle = 1;
            } else {
                node.style("opacity", 1);
                link.style("opacity", 1);
                toggle = 0;
            }

        }
}
//Refrescar Grafico
function refrescarGrafico(valor) {
    var nodosFiltrados = datosTotales.nodes.filter(checkNumSeguidores);

    // Filtro por tipo de usuario (verificado/no verificado)
	if (valor === 'VERIFICADOS') {
	    nodosFiltrados = nodosFiltrados.filter(checkVerificados);
    } else if (valor === 'NO_VERIFICADOS') {
	    nodosFiltrados = nodosFiltrados.filter(checkNoVerificados);
    }

    pintarGrafo('betweenness', nodosFiltrados);

}

// Selecciona el nº de seguidores del filtro
function seleccionarNumeroSeguidores() {
	document.getElementById('valorNumeroSeguidores').innerHTML = document.getElementById('num_followers').value.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
	refrescarGrafico();
}


//Radiobuttons Selecciona el Tipo de Usuario
function seleccionarTipoUsuario(valor) {
    refrescarGrafico(valor);
}