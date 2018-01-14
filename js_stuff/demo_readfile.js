/* the require() function is a built in module required to create a server*/
var http = require('http');
var fs = require('fs'); /*filesystem module that allows you to read, create, update,
delete and rename files*/

// create a server object with createServer()
http.createServer(function (req, res) {
	fs.readFile('readfile_example.html', function(err, data) { 
	// above line reads the file and returns data
		res.writeHead(200, {'Content-Type': 'text/html'});
		res.write(data);
		res.end();
	});

}).listen(8080); // the server object listens on port 8080

