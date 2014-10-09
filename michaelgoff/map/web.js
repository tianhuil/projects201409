// The CitiBike mapping application

var express = require('express');
var bodyParser = require('body-parser');
var cookieParser = require('cookie-parser');
var session = require('express-session');
var sys = require("sys"), fs = require("fs");
var flash = require('connect-flash');
var parse = require('csv-parse');

var app = express();

app.use(bodyParser());
app.use(cookieParser());
app.use(session({ secret: 'SECRET' }));
app.use(flash());

var page = "";

app.get('/', function(request, response) {
	var blocks = fs.readFileSync("index.html","utf8").split("***");
	response.send(blocks[0] + "var init_code = ''" + blocks[1]);
});

app.get('/:code', function(request, response) {
	var blocks = fs.readFileSync("index.html","utf8").split("***");
	response.send(blocks[0] + "var init_code = '" + request.params.code.toString() + "'" + blocks[1]);
});

app.post('/get_data', function(request,response) {
	var item = data[request.body.station];
	ret = "Station: " + item.id + "<br>" +
	      "Coordinates: (" + item.lat + "," + item.lon + ")<br>" +
		  "Average Daily Usage: " + item.COUNT / 335.0;
	response.send(ret);
});

app.post('/get_station_dests', function(request,response) {
	response.send(JSON.stringify(data[request.body.station]));
});

app.post('/get_station_origins', function(request,response) {
	var stat = request.body.station;
	var ret = {};
	for (key in data) {
		ret[key] = data[key][stat.toString()];
	}
	ret['COUNT'] = data[stat]['COUNT'];
	response.send(JSON.stringify(ret));
});

app.post('/get_projections', function(request,response) {
	var ret = {existing: {}, proposed: []};
	for (key in projections) {
		if (key < 10000) {
			ret.existing["station"+key] = projections[key]['gain'] + data[key]['COUNT'];
		}
		else {
			ret.proposed.push(projections[key]['proj']);
		}
	}
	response.send(JSON.stringify(ret));
});

app.post('/station_data', function(request,response) {
	var ret = {};
	for (key in data) {
		ret["station"+key] = [];
		for (p in request.body) {ret["station"+key].push(data[key][request.body[p]])}
	}
	response.send(JSON.stringify(ret));
});

app.post('/load_stations', function(request,response) {
	var ret = {};
	for (key in data) {
		ret["station"+key] = {stat: "existing", lat:data[key].lat, lon:data[key].lon, num:key};
	}
	for (var i=0; i<proposed.length; i++) {
		ret["p"+i] = {stat:"proposed", lat:proposed[i].lat, lon:proposed[i].lon, num:i}
	}
	response.send(JSON.stringify(ret));
});

app.post('/census_data',function(request,response) {
	var fields = JSON.parse(request.body.fields);
	var ret = {};
	for (key in census) {
		ret[key] = {shape: census[key].points};
		for (field in fields) {ret[key][fields[field]] = census[key][fields[field]]};
	}
	response.send(JSON.stringify(ret));
});

var data = {};
var proposed = [];
var census = {};
var projections = {};
// Initialize variables
function Init() {
	parse(fs.readFileSync("station_data.csv","utf8"), function(err, output) {
		var markers = ""; // Markers that go into the Google Map
		for (var i=1; i<output.length; i++) {
			output[i][0] = parseInt(output[i][0]);
			var new_obj = {}; // Here we convert the array into a dictionary with keys given by the first row of the CSV file
			for (var j=0; j<output[0].length; j++) {
				new_obj[output[0][j]] = output[i][j];
			}
			new_obj['lat'] = parseFloat(new_obj['lat']);
			new_obj['lon'] = parseFloat(new_obj['lon']);
			new_obj['COUNT'] = parseInt(new_obj['COUNT']);
			data[new_obj['id']] = new_obj;
	    }
		page = fs.readFileSync("index.html","utf8");
	});
	parse(fs.readFileSync("new_stations.csv","utf8"), function(err,output) {
		for (var i=1; i<output.length; i++) {
			output[i][0] = parseInt(output[i][0]);
			var new_obj = {}; // Here we convert the array into a dictionary with keys given by the first row of the CSV file
			for (var j=0; j<output[0].length; j++) {
				new_obj[output[0][j]] = output[i][j];
			}
			new_obj['lat'] = parseFloat(new_obj['lat']);
			new_obj['lon'] = parseFloat(new_obj['lon']);
			proposed.push(new_obj);
	    }	
	});
	parse(fs.readFileSync("all_blockgroups.csv","utf8"), function(err, output) {
		for (var i=1; i<output.length; i++) {
			var new_obj = {};
			for (var j=1; j<output[0].length; j++) {
				new_obj[output[0][j]] = output[i][j];
			}
			census[new_obj['block_tract']] = new_obj;
		}
	});
	parse(fs.readFileSync("projections.csv","utf8"), function(err,output) {
		var ids = output[0];
		for (var i=1; i<output.length; i++) {
			var new_obj = {};
			for (var j=1; j<output.length+2; j++) {
				new_obj[ids[j]] = parseFloat(output[i][j]);
			}
			projections[ids[i]] = new_obj;
		}
	});
}

var port = process.env.PORT || 8080;
app.listen(port, function() {
  console.log("Listening on " + port);
  Init();
});
