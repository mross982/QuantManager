/* the require() function is a built in module required to create a server*/
var http = require('http');
var dt = require('./firstModule'); /*New module created in another file*/
var url = require('url');

// create a server object with createServer()
http.createServer(function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/html'});
    /*the first argument of the writeHead() method is the status code, 200 means OK,
    the second argument is an object containing the response headers.*/

    var q = url.parse(req.url, true).query;
	var txt = q.year + " " + q.month
    // in the url, enter 'http://localhost:8080/?year=2018&month=January'

    res.end(txt); // end the response
}).listen(8080); // the server object listens on port 8080

