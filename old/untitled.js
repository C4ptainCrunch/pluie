nlWeather: {
    bounds: [[53.749, 3.125], [50.681, 7.598]]
},
nlRadar: {
    bounds: [[54.8, 0], [49.5, 10]]
},
beRadar: {
    bounds: [[52.5, 1], [49.1, 7]]
},
euRadar: {
    bounds: [[60, -11], [42, 20]]
},
euGfs: {
    bounds: [[71.5, -43], [28, 52]]
}


http://api.buienradar.nl/image/1.0/webmercatorcloudnl/png/?t=201605092215&w=1100&h=953&nc=1
http://api.buienradar.nl/image/1.0/webmercatorsunnl/png/?t=201605092105&w=1100&h=953&nc=1
http://api.buienradar.nl/image/1.0/webmercatorradarnl/png/?t=201605091625&w=1100&h=953&nc=1

http://jsfiddle.net/Pe5xU/548/


// Create the map
var map = L.map('map').setView([50, 4], 6);

// Set up the OSM layer
L.tileLayer(
    'http://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
    {maxZoom: 18}).addTo(map);

L.marker([54.8, 0]).addTo(map);
L.marker([49.5, 10]).addTo(map);

var imageUrl = 'http://api.buienradar.nl/image/1.0/webmercatorradarnl/png/?t=201605091625',
    imageBounds = [[54.8, 0], [49.5, 10]];

L.imageOverlay(imageUrl, imageBounds, {opacity: 0.9}).addTo(map);
