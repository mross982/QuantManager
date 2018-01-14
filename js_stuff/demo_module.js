/* the require() function is a built in module required to create a server*/
var http = require('http');
var dt = require('./MyModule') /*New module created in another file*/

// create a server object with createServer()
http.createServer(function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/html'});
    /*the first argument of the writeHead() method is the status code, 200 means OK,
    the second argument is an object containing the response headers.*/
    res.write("The date and time are currently: " + dt.myDateTime());
    res.write('Hello World!') // write a response to the client
    res.end(); // end the response
}).listen(8080); // the server object listens on port 8080

