/* the require() function is a built in module required to create a server*/
var http = require('http');
var fs = require('fs'); /*filesystem module that allows you to read, create, update,
delete and rename files*/

// create a server object with createServer()
http.createServer(function (req, res) {
	
	/*fs module has methods for creating files: fs.appendFile(), fs.open(), fs.writeFile()*/
	fs.appendFile('mynewfile1.txt', 'Hello content!', function (err){
		if (err) throw err;
		console.log('Saved!'); // this is printed to the command line
	});

	/*the open() method takes a 'Flag' as the second argument, if the flag is 'w' for 'writing', the
	specified file is opend for writing. If the file does not exist, an empty file is created.*/
	fs.open('mynewfile2.txt', 'w', function (err, file){
		if (err) throw err;
		console.log('Saved!');
	});
    
    /* the writeFile() method replaces the specified file and content if it exists. If the file does not
    exist, a new file, containing the specified content, will be created.*/
    fs.writeFile('mynewfile3.txt', 'Hello Content!', function (err) {
    	if (err) throw err;
    	console.log('Saved!');
    });


}).listen(8080); // the server object listens on port 8080

