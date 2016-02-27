
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xml:lang="en" xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
  <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
  <script type="text/javascript" src="//code.jquery.com/jquery-git.js"></script>  

  <title>Highcharts test tool by highcharts</title>
<script type='text/javascript'>
function updateGraph(){
	$(function(){
		var pitTemps = [];
		var foodTemps = [];
		var x_values = [];
		var temp = 0;
		var timeStr;
		
		$.get('gpio.php', { mode:"graph" }, function(data) {
				data = data.split('/');
				var tempSwitch = false;
				for (var i in data)
				{
					if (tempSwitch == false)
					{
						pitTemps.push(parseInt(data[i]));
						tempSwitch = true;
					}
					else
					{
						foodTemps.push(parseInt(data[i]));
						tempSwitch = false;
					}
					timeStr = Math.floor(temp/3600) + 'h ' + Math.floor((temp % 3600)/60) 
							+ 'm ' + (temp % 60) + "s";
					x_values.push(timeStr);
					temp = temp + 5;
				}
				pitTemps.pop();
				
				$('#container').highcharts({
					chart : {
						type : 'line',
						zoomType: 'x'
					},
					title : {
						text : 'Smoker Temperature'
					},
					xAxis : {
						title : {
							text : 'Time'
						},
						categories : x_values
					},
					yAxis : {
						title : {
							text: 'Temperature'
						}
					},
					series: [{
						name : 'Brisket Temperature',
						data : foodTemps
					},{
						name : 'Pit Temp',
						data : pitTemps
					}],
				});
			}
		)
	});
}

function updateTableData(){
	var request = new XMLHttpRequest();
	request.open( "Get" , "gpio.php", true);
	request.send(null);
	request.onreadystatechange = function () {
		if(request.readyState == 4 && request.status == 200){
			data = request.responseText;
			var splitData = data.split(",");
			document.getElementById("pitTemp").innerHTML = splitData[0];
			document.getElementById("foodTemp").innerHTML = splitData[1];
			document.getElementById("setTemp").innerHTML = splitData[2];
			if(splitData[3] == 1){
				document.getElementById("fan").innerHTML = "On";}
			else{
				document.getElementById("fan").innerHTML = "Off";}
			document.getElementById("fanCount").innerHTML = convertTime(splitData[4]);
		}
	}
}

function convertTime(count){
	var seconds = count * 5;
	var minutes = Math.floor(seconds/60);
	seconds = seconds % 60;
	var result = minutes + 'm ' + seconds + 's';
	return result;
}
	

updateTableData();
updateGraph();
setInterval(function(){
	updateTableData();
}, 5000);

setInterval(function(){
	updateGraph();
}, 60000);

function updateSetPoint(){
	var tempSetPoint = document.getElementById('newSetTemp').value;
	$.get('setTemp.php', { setTemp: tempSetPoint });
	alert("New fan set point: " + tempSetPoint);
	document.getElementById('newSetTemp').value = "";
	document.getElementById('setTemp').innerHTML = tempSetPoint;
}

</script>
<style>
h1 {
    font-family: "Arial";
    font-size: 30px;
}

td {
    font-family: "Arial";
    font-size: 35px;
	text-align: center;
}

table {
    border-collapse: collapse;
}
</style>
</head>
<body>
  <script src="http://code.highcharts.com/highcharts.js"></script>
	<H1 id="p1">Smoker Data Output</H1>
	<table border="1">
		<tr>
			<td>Pit Temp</td><td>Brisket Temp</td><td>Fan Set Temp</td><td>Fan Status</td><td>Fan Count</td>
		</tr>
		<tr>
			<td id="pitTemp"></td>
			<td id="foodTemp"></td>
			<td id="setTemp"></td>
			<td id="fan"></td>
			<td id="fanCount"></td>			
		</tr>
		
	</table>
	<br>
	<br>
	<div>
		<input type="text" name="newSetTemp" id="newSetTemp">
		<button onclick="updateSetPoint()">Update Set Point</button>
	</div>
	<div id="container" style="height: 500px"></div>
</body>
</html>

