var express = require('express');
var http = require('http');
var path = require('path');
var bodyParser = require('body-parser');
var engine = require('ejs-locals');

var app = express();

// Parse URL-encoded bodies (as sent by HTML forms)
app.use(express.urlencoded({
    extended: true
}));;

app.use(bodyParser.urlencoded({
    extended: false
}));

// Set up ejs templating.
app.engine('ejs', engine);
app.set('view engine', 'ejs');

// Enable routing and use port 8080
require('./router')(app);
app.set('port', 8080);

// Parse JSON bodies (as sent by API clients)
app.use(express.json());

// Set view folder.
app.set('views', path.join(__dirname, '/views'));

// set public folder
app.use(express.static(__dirname + '/public'));

http.createServer(app).listen(app.get('port'), () => {
    console.log('Server listening on port ' + app.get('port'));
});