// Funcion auxiliar para mostrar datos por consola
function imprimir(datos) {
    console.log('imprimir: ' + datos);
//    JSON.stringify(datos);
}

// Control del menu izquierdo
function abrirMenuIzquierdo(){
    document.getElementById("leftNav").style.width ="250px";
}

function cerrarMenuIzquierdo(){
    document.getElementById("leftNav").style.width="0";
}

// Funciones para el buscador
// function cambioHashtag() {
//     var hashtag = document.getElementById('hashtag').value;
//     if (!hashtag) {
//         document.getElementById('botonBuscar').disabled = true;
//     } else {
//         document.getElementById('botonBuscar').disabled = false;
//     }
// }
function buscarHashtag() {
    var url = "/datos?hashtag=" + document.getElementById('hashtag').value;
    alert("Se llamara " + url);
/*
    $.ajax({
       url: url,
       success: function(response) {
           console.log('retorno del ajax');
       }
    });
*/
}


// Popup de informacion
function mostrarModalUsuarios() {
    $("#infoUsuariosModal").modal();
}

// Control del menu derecho (Boton Top)
function abrirDerecho() {
    var anchoActual = document.getElementById("rightNav").style.width;
    if (anchoActual === '350px') {
        document.getElementById("rightNav").style.width = '0px';
        $('#btnMostrarTop span').addClass('glyphicon-chevron-left');
        $('#btnMostrarTop span').removeClass('glyphicon-chevron-right');
    } else {
        document.getElementById("rightNav").style.width = '350px';
        $('#btnMostrarTop span').removeClass('glyphicon-chevron-left');
        $('#btnMostrarTop span').addClass('glyphicon-chevron-right');
    }
}

function cerrarDerecho() {
    document.getElementById("rightNav").style.width = '0px';
}



// Controles del formulario (sliders, checkboxes, botones de algoritmos...)

function checkNumSeguidores(node){
    return node.num_followers >= document.getElementById('num_followers').value;
}
function checkVerificados(node){
    return node.verified == true;
}
function checkNoVerificados(node){
    return node.verified == false;
}

// Modal de algoritmos
function mostrarModalAlgoritmos() {
    $("#algoritmosModal").modal();
}


// Carga de la tabla del menu derecho
function calcularTablaTopRating(nombreJson) {
    $.getJSON(nombreJson, function (data) {
        var arrItems = [];      // THE ARRAY TO STORE JSON ITEMS.
        $.each(data, function (index, value) {
            arrItems.push(value);       // PUSH THE VALUES INSIDE THE ARRAY.
        });

        var col = [];
        for (var i = 0; i < arrItems.length; i++) {
            for (var key in arrItems[i]) {
                if (col.indexOf(key) === -1) {
                    col.push(key);
                }
            }
        }

        var table = document.createElement("table");

        var tr = table.insertRow(-1);

        for (var i = 0; i < col.length; i++) {
            var th = document.createElement("th");
            th.innerHTML = col[i];
            tr.appendChild(th);
        }

        for (var i = 0; i < arrItems.length; i++) {

            tr = table.insertRow(-1);

            for (var j = 0; j < col.length; j++) {
                var tabCell = tr.insertCell(-1);
                tabCell.innerHTML = arrItems[i][col[j]];
            }
        }

        var divContainer = document.getElementById("insertarDatos");
        divContainer.innerHTML = "";
        divContainer.appendChild(table);
    });
}

// Funcion para sacar los valores unicos de los arrays
Array.prototype.unique=function(a){
  return function(){return this.filter(a)}}(function(a,b,c){return c.indexOf(a,b+1)<0
});

// Función para sacar las comunidades que genera Louvain
function comunidadesLouvain(nodos){
    var louvainList=[];
    for(var i=0; i< nodos.length; i++){
        louvainList.push(nodos[i].louvain)
    }
    return louvainList.sort().unique();
}

// Funcion para sacar las comunidades que genera Connected Components
function comunidadesComponentesConexas(nodos){
    var componentsList=[];
    for(var i=0; i< nodos.length; i++){
        componentsList.push(nodos[i].partition)
    }
    return componentsList.sort().unique();
}
// Funcion que se ejecuta cuando la pagina se ha cargado
$(document).ready(function(){

    // Carga los tooltips de la pagina
    $('[data-toggle="tooltip"]').tooltip();

});

