/* the require() function is a built in module required to create a server*/
var http = require('http');
var fs = require('fs'); /*filesystem module that allows you to read, create, update,
delete and rename files*/

// create a server object with createServer()
http.createServer(function (req, res) {
	// fs.unlink('filename', function(err{if (err) throw err:})) #deletes the file
	fs.unlink('mynewfile2.txt', function (err) {
		if (err) throw err;
		console.log('file deleted!')
	})

	fs.rename('mynewfile1.txt', 'myrenamedfile.txt', function (err) { //Renames the file
  		if (err) throw err;
  		console.log('File Renamed!')
  	})

}).listen(8080); // the server object listens on port 8080

