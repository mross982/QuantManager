/* the require() function is a built in module required to create a server*/
var http = require('http');

// create a server object with createServer()
http.createServer(function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/html'});
    /*the first argument of the writeHead() method is the status code, 200 means OK,
    the second argument is an object containing the response headers.*/
    
    
    
}).listen(8080); // the server object listens on port 8080

