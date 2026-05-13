<template>
    <div>

        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />

            <!-- Styles -->
            <!-- Bootstrap -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

            <!-- Font Awesome -->
            <link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet" />

            <!-- OpenLayers library -->
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ol@v8.1.0/ol.css">

            <!-- Styles for the application -->
            <!-- <link rel="stylesheet" href="./styles/viewer.css" type="text/css"/> -->

            <!-- Application icon -->
            <!-- <link rel="icon" href="./images/favicon.png" type="image/png"> -->

            <title>Burundi | Market Analytics</title>
        </head>

        <body onload="init()">

            <nav class="navbar navbar-expand-lg bg-light navbar-light fixed-top">
                <div class="container-fluid">
                    <a class="navbar-brand" href="index.html"><strong>Burundi</strong> | Market Analytics</a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                        data-bs-target="#collapsibleNavbar">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="collapsibleNavbar">
                        <ul class="navbar-nav">
                            <li class="nav-item">
                                <a class="nav-link" href="#" onclick="showPanel('pnl-basemap')">Base layer</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="#" onclick="showPanel('pnl-search')">Search</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="#" onclick="showPanel('pnl-service')">Service area</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="#" onclick="showPanel('pnl-closest')">Closest market</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="#" onclick="showPanel('pnl-route')">Shortest route</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="#" onclick="clearResults()">Clear results</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>

            <div id="pnl-closest" class="card panel panel-tool">
                <div class="card-header">
                    Closest market
                    <span class="pull-right clickable close-icon" data-effect="fadeOut"><i
                            class="fa fa-times"></i></span>
                </div>
                <div class="card-body">
                    <div id="pnl-closest-alert" class="alert alert-danger">
                        Error:
                    </div>
                    <form>
                        <div class="form-group">
                            <label for="location-closest">Location</label>
                            <input id="location-closest" type="textbox" class="form-control"
                                placeholder="Click here and then on the map">

                            <input id="btnClosest" type="button" class="btn pull-right" value="Find market">
                        </div>
                    </form>
                </div>
            </div>

            <div id="pnl-route" class="card panel panel-tool">
                <div class="card-header">
                    Shortest route
                    <span class="pull-right clickable close-icon" data-effect="fadeOut"><i
                            class="fa fa-times"></i></span>
                </div>
                <div class="card-body">
                    <div id="pnl-route-alert" class="alert alert-danger">
                        Error:
                    </div>
                    <form>
                        <div class="form-group">
                            <label for="start">Start</label>
                            <input id="start" type="textbox" class="form-control"
                                placeholder="Click here and then on the map">
                            <label for="start">End</label>
                            <input id="end" type="textbox" class="form-control"
                                placeholder="Click here and then on the map">
                            <input id="btnRoute" type="button" class="btn pull-right" value="Find route">
                        </div>
                    </form>
                </div>
            </div>

            <div id="pnl-search" class="card panel panel-tool">
                <div class="card-header">
                    Search markets
                    <span class="pull-right clickable close-icon" data-effect="fadeOut"><i
                            class="fa fa-times"></i></span>
                </div>
                <div class="card-body">
                    <div id="pnl-search-alert" class="alert alert-danger">
                        Error:
                    </div>
                    <form>
                        <div class="form-group">
                            <label for="location-search" class="form-label">Location</label>
                            <input id="location-search" type="textbox" class="form-control"
                                placeholder="Click here and then on the map" />
                        </div>
                        <div class="form-group">
                            <label for="distance-slider" class="form-label">Distance to search: <spam id="val">0</spam>
                                km</label>
                            <input id="distance-slider" type="range" class="form-range" min="0" max="50" step="0.1"
                                value="0" />
                        </div>
                        <div class="form-group">
                            <input id="btnSearch" type="button" class="btn pull-right" value="Search">
                        </div>
                    </form>
                </div>
            </div>

            <div id="pnl-service" class="card panel panel-tool">
                <div class="card-header">
                    Service area
                    <span class="pull-right clickable close-icon" data-effect="fadeOut"><i
                            class="fa fa-times"></i></span>
                </div>
                <div class="card-body">
                    <div id="pnl-service-alert" class="alert alert-danger">
                        Error:
                    </div>
                    <form>
                        <div class="form-group">
                            <label for="location-service">Location</label>
                            <input id="location-service" type="textbox" class="form-control"
                                placeholder="Click here and then on the map" />
                        </div>
                        <div class="form-group">
                            Size of market:
                            <div class="form-check">
                                <input id="small_market" type="radio" name="size" class="form-check-input"
                                    value="small_areas" checked /><label for="small_market">Small market</label>
                            </div>
                            <div class="form-check">
                                <input id="local_market" type="radio" name="size" class="form-check-input"
                                    value="local_areas" /><label for="local_market">Local market</label>
                            </div>
                            <div class="form-check">
                                <input id="medium_market" type="radio" name="size" class="form-check-input"
                                    value="medium_areas" /><label for="medium_market">Medium market</label>
                            </div>
                            <div class="form-check">
                                <input id="capital_market" type="radio" name="size" class="form-check-input"
                                    value="capital_areas" /><label for="capital_market">Capital market</label>
                            </div>
                        </div>
                        <div class="form-group">
                            <input id="btnService" type="button" class="btn pull-right" value="Find area">
                        </div>
                    </form>
                </div>
            </div>

            <div id="pnl-basemap" class="card panel panel-tool">
                <div class="card-header">
                    Base layer
                    <span class="pull-right clickable close-icon" data-effect="fadeOut"><i
                            class="fa fa-times"></i></span>
                </div>
                <div class="card-body">
                    <form>
                        <div class="form-group">
                            <div class="form-check">
                                <input id="base-osm" type="radio" name="basemap" class="form-check-input" value="osm"
                                    checked /><label for="base-osm">OpenStreetMap</label>
                            </div>
                            <div class="form-check">
                                <input id="base-otm" type="radio" name="basemap" class="form-check-input"
                                    value="otm" /><label for="base-otm">OpenTopoMap</label>
                            </div>
                            <div class="form-check">
                                <input id="base-esri-wtm" type="radio" name="basemap" class="form-check-input"
                                    value="esri_wtm" /><label for="base-esri-wtm">ESRI World Topo Map</label>
                            </div>
                            <div class="form-check">
                                <input id="base-esri-natgeo" type="radio" name="basemap" class="form-check-input"
                                    value="esri_natgeo" /><label for="base-esri-natgeo">ESRI NatGeo World Map</label>
                            </div>
                            <div class="form-check">
                                <input id="base-own" type="radio" name="basemap" class="form-check-input"
                                    value="own" /><label for="base-own">Own tile service</label>
                            </div>
                        </div>
                    </form>
                </div>
            </div>


            <div id="pnl-about" class="card panel panel-info">
                <div class="card-header">
                    <strong>About</strong>
                    <span class="pull-right clickable close-icon" data-effect="fadeOut"><i
                            class="fa fa-times"></i></span>
                </div>
                <div class="card-body">
                    <p class="card-text">
                        This web application was developed as an academic exercise for the students of the course "Geo
                        web app building with open-source GIS tools".
                        <br /><br />
                        Attributions:
                    <ul>
                        <li>Landing page background: Photo by <a
                                href="https://unsplash.com/@organicdesignco?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash"
                                target="blank">Megan Thomas</a> on <a
                                href="https://unsplash.com/photos/bundle-of-assorted-vegetable-lot-xMh_ww8HN_Q?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash"
                                target="blank">Unsplash</a>
                        </li>
                        <li>Location marker: Vectors and icons by <a href="https://www.svgrepo.com" target="blank">SVG
                                Repo</a></li>
                        <li>Market marker: <a href="https://www.flaticon.com/free-icons/market" target="blank"
                                title="market icons">Market icons created by mynamepong - Flaticon</a></li>
                    </ul>
                    </p>
                </div>
            </div>

            <div id="pnl-contact" class="card panel panel-info">
                <div class="card-header">
                    <strong>Contact</strong>
                    <span class="pull-right clickable close-icon" data-effect="fadeOut"><i
                            class="fa fa-times"></i></span>
                </div>
                <div class="card-body">
                    <p class="card-text">
                        For information about the <strong>Faculty ITC</strong> visit <a
                            href="https://www.itc.nl/">www.itc.nl</a>. <br /><br />
                        You can contact the instructors via e-mail:
                    <ul>
                        <li><strong>Gustavo García:</strong> <a
                                href="mailto:g.a.garciachapeton-1@utwente.nl">g.a.garciachapeton-1@utwente.nl</a></li>
                        <li><strong>Lucas de Oto:</strong> <a
                                href="mailto:l.h.deoto@utwente.nl">l.h.deoto@utwente.nl</a></li>
                    </ul>
                    </p>
                </div>
            </div>

            <div id="map">

            </div>

            <footer class="fixed-bottom bg-light">
                <div class="container-fluid d-flex justify-content-center">
                    <a href="#" onclick="showPanel('pnl-about')">About</a>
                    <a href="#" onclick="showPanel('pnl-contact')">Contact</a>

                </div>
            </footer>
            <!-- Scripts -->
            <!-- JQuery library -->
            <script src="https://code.jquery.com/jquery-3.7.1.min.js"
                integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo=" crossorigin="anonymous"></script>

            <!-- Bootstrap -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

            <!-- Openlayers -->
            <script src="https://cdn.jsdelivr.net/npm/ol@v8.1.0/dist/ol.js"></script>

            <!-- Own script -->
            <script src="./scripts/viewer.js"></script>


        </body>
    </div>
</template>

<script setup>
let mainMap = null;

let currentElement = "";

$("input[type=textbox]").focus(function () {
    currentElement = $(this).attr("id");
});

$("#distance-slider").on("input", function () {
    $('#val').text($("#distance-slider")[0].value);
    drawCircle();
});

function drawCircle() {
    centroid = $("#" + currentElement).val().split(",");
    centroid = [parseFloat(centroid[0]), parseFloat(centroid[1])];
    radious = parseFloat($("#val").text());

    let circle = new ol.geom.Circle(centroid, radious * 1000.0);

    const vectorSource = new ol.source.Vector({
        features: [new ol.Feature(circle)],
    });

    const vectorLayer = new ol.layer.Vector({
        name: "circle",
        source: vectorSource,
        style: new ol.style.Style({
            stroke: new ol.style.Stroke({
                color: '#ff0000',
                width: 2,
            }),
            fill: new ol.style.Fill({
                color: 'rgba(255, 255, 255, 0.4)'
            })
        })
    });

    removeLayerByName(mainMap, "circle");
    mainMap.addLayer(vectorLayer);
}
function init() {
    // Define the map view
    let mainView = new ol.View({
        extent: [3124925, -599644, 3537136, -158022],
        center: [3336467, -385622],
        minZoom: 6,
        maxZoom: 14,
        zoom: 9
    });


    // Initialize the map
    mainMap = new ol.Map({
        controls: [],
        target: 'map', /* Set the target to the ID of the map*/
        view: mainView,
        controls: []
    });

    let baseLayer = getBaseMap("osm");

    mainMap.addLayer(baseLayer);

    mainMap.on('click', function (evt) {
        let val = evt.coordinate[0].toString() + "," + evt.coordinate[1].toString();
        if (currentElement != "") {
            $("#" + currentElement).val(val);

            let name = "location_1";
            let color = "#FF0000";

            if (currentElement == 'end') {
                name = "location_2";
                color = "#00FF00";
            }

            const feature = new ol.Feature({
                geometry: new ol.geom.Point([evt.coordinate[0], evt.coordinate[1]]),
            });

            feature.setStyle(
                new ol.style.Style({
                    image: new ol.style.Icon({
                        color: color,
                        src: './images/pin.svg',
                        width: 30,
                    })
                })
            );

            const layer = new ol.layer.Vector({
                name: name,
                source: new ol.source.Vector({
                    features: [feature],
                })
            });
            layer.setZIndex(100);

            removeLayerByName(mainMap, name);
            mainMap.addLayer(layer);

            if (currentElement == "location-search") {
                drawCircle();
            }
        }
    })
}

function getBaseMap(name) {
    let baseMaps = {
        "osm": {
            url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            attributions: ''
        },
        "otm": {
            url: 'https://b.tile.opentopomap.org/{z}/{x}/{y}.png',
            attributions: 'Kartendaten: © OpenStreetMap-Mitwirkende, SRTM | Kartendarstellung: © OpenTopoMap (CC-BY-SA)'
        },
        "esri_wtm": {
            url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
            attributions: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community'
        },
        "esri_natgeo": {
            url: 'https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}',
            attributions: 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC'
        },
        "own": {
            url: 'b_tiles/{z}/{x}/{y}.png'
        }
    }

    layer = baseMaps[name];
    if (layer === undefined) {
        layer = baseMaps["osm"]
    }

    return (
        new ol.layer.Tile({
            name: "base",
            source: new ol.source.TileImage(layer)
        })
    )
}

function hidePanels() {
    $(".panel").hide();
    $(".alert").hide();
    clearResults();
}

function clearResults() {
    $("input[type=textbox]").val("");
    currentElement = "";
    layers = ["location_1", "location_2", "route", "markets", "area", "circle"];
    for (let i = 0; i < layers.length; i++)
        removeLayerByName(mainMap, layers[i]);
}

function showPanel(id) {
    hidePanels();
    $("#" + id).show();
}

$('.close-icon').on('click', function () {
    $(this).closest('.card').fadeOut();
})


function removeLayerByName(map, layer_name) {
    let layerToRemove = null;
    map.getLayers().forEach(function (layer) {
        if (layer.get('name') != undefined && layer.get('name') === layer_name) {
            layerToRemove = layer;
        }
    });

    map.removeLayer(layerToRemove);
}

$("input[name=basemap]").click(function (evt) {
    removeLayerByName(mainMap, "base");
    let baseLayer = getBaseMap(evt.target.value);
    mainMap.addLayer(baseLayer);
})

$("#btnService").click(function () {
    removeLayerByName(mainMap, "area");
    $("#pnl-service-alert").hide();

    $.ajax({
        url: "http://localhost:8000/cgi-bin/service_area.py?" +
            "location=" + $("#location-service").val() +
            "&size=" + $("input[name=size]:checked")[0].value +
            "&srid=3857",
        type: "GET",
        success: function (data) {
            if (data.length != 0) {
                // console.log('data length: ', data.length);
                console.log('first data geom: ', data);
                let vectorLayer = new ol.layer.Vector({
                    name: "area",
                    source: new ol.source.Vector({
                        features: new ol.format.GeoJSON().readFeatures(data[0].geom),
                    }),
                    style: new ol.style.Style({
                        stroke: new ol.style.Stroke({
                            color: '#ff0000',
                            width: 2,
                        }),
                        fill: new ol.style.Fill({
                            color: 'rgba(255, 255, 255, 0.4)'
                        })
                    })
                });

                mainMap.addLayer(vectorLayer);
            }
        },
        error: function (data) {
            $("#pnl-service-alert").html("Error: An error occurred while executing the tool.");
            $("#pnl-service-alert").show();
        }
    })
});

const sizes = {
    "small_markets": 15,
    "local_markets": 20,
    "medium_markets": 25,
    "capital_markets": 40
};

$("#btnSearch").click(function () {
    removeLayerByName(mainMap, "markets");
    $("#pnl-search-alert").hide();

    $.ajax({
        url: "http://localhost:8000/cgi-bin/search.py?location=" +
            $("#location-search").val() +
            "&distance=" +
            $("#val").text() +
            "&srid=3857",
        type: "GET",
        success: function (data) {
            console.log('data : ', data);
            if (data.length != 0) {
                let features = [];
                for (var i = 0; i < data.length; i++) {
                    var feature = new ol.format.GeoJSON().readFeature(data[i].geom);
                    feature.setStyle(
                        new ol.style.Style({
                            image: new ol.style.Icon({
                                src: './images/market.png',
                                width: sizes[data[i].categorie]
                            })
                        })
                    );
                    features.push(feature);
                }

                const vectorSource = new ol.source.Vector({
                    features: features,
                })

                const vectorLayer = new ol.layer.Vector({
                    name: "markets",
                    source: vectorSource,
                })

                mainMap.addLayer(vectorLayer)
            }
        },
        error: function (data) {
            $("#pnl-search-alert").html("Error: An error occurred while executing the tool.");
            $("#pnl-search-alert").show();
        }
    })
});

$("#btnRoute").click(function () {
    removeLayerByName(mainMap, "route");
    $("#pnl-route-alert").hide();

    $.ajax({
        url: "http://localhost:8000/cgi-bin/routing.py?source=" +
            $("#start").val() +
            "&target=" +
            $("#end").val() +
            "&srid=3857",
        type: "GET",
        success: function (data) {
            if (data.path != null) {
                console.log('data : ', data);
                let vectorLayer = new ol.layer.Vector({
                    name: "route",
                    source: new ol.source.Vector({
                        features: new ol.format.GeoJSON().readFeatures(data.path),
                    }),
                    style: new ol.style.Style({
                        stroke: new ol.style.Stroke({
                            color: '#ff0000',
                            width: 4,
                        }),
                    })
                });
                mainMap.addLayer(vectorLayer);

            }
        },
        error: function (data) {
            $("#pnl-route-alert").html("Error: An error occurred while executing the tool.");
            $("#pnl-route-alert").show();
        }
    })
});

$("#btnClosest").click(function () {
    removeLayerByName(mainMap, "markets");
    $("#pnl-closest-alert").hide();

    $.ajax({
        url: "http://localhost:8000/cgi-bin/closest_markets.py?location=" +
            $("#location-closest").val() +
            "&srid=3857",
        type: "GET",
        success: function (data) {
            if (data.length != 0) {
                let features = [];
                for (var i = 0; i < data.length; i++) {
                    var feature = new ol.format.GeoJSON().readFeature(data[i].geometry);
                    feature.setStyle(
                        new ol.style.Style({
                            image: new ol.style.Icon({
                                src: './images/market.png',
                                width: sizes[data[i].categorie]
                            })
                        })
                    );
                    features.push(feature);
                }

                const vectorSource = new ol.source.Vector({
                    features: features,
                })

                const vectorLayer = new ol.layer.Vector({
                    name: "markets",
                    source: vectorSource,
                })

                mainMap.addLayer(vectorLayer)
            }
        },
        error: function (data) {
            $("#pnl-closest-alert").html("Error: An error occurred while executing the tool.");
            $("#pnl-closest-alert").show();
        }
    })
});

// // Hide all panels and alerts on page load
// $(document).ready(function() {
//     hidePanels();
// });
</script>

<style scoped>
.nav-item a:hover {
    background-color: rgb(107, 168, 67);
    color: white;
}

#map {
    position: absolute;
    top: 0px;
    bottom: 0px;
    left: 0px;
    right: 0px;
}

footer {
    padding: 0px;
}

footer a {
    text-decoration: none;
    color: rgb(94, 94, 94);
    padding: 5px 20px;
}

footer a:hover {
    background-color: rgb(107, 168, 67);
    color: white;
}


/* •  •  • */

.panel {
    display: none;
    position: absolute;
    height: auto;
    z-index: 100;
}

.panel-tool {
    width: 350px;
    right: 5px;
    top: 70px;
}

.panel-tool input[type=button] {
    background-color: rgb(107, 168, 67);
    color: white;
    margin-top: 10px;
    margin-bottom: 10px;
}

.panel-info {
    max-width: 450px;
    bottom: 50px;
}

#pnl-contact {
    left: 50%;
}

#pnl-about {
    right: 50%;
}


.panel .card-header {
    background-color: rgb(107, 168, 67);
    color: white;
}

.close-icon {
    cursor: pointer;
}
</style>