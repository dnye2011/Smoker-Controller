<?php

	if ($_GET['mode'] == 'graph'){
		$today = getdate();
		if (strlen($today['mon']) == 1){
			$month = "0" . $today['mon'];
		}
		else{
			$month = $today['mon'];
		}
		if (strlen($today['mday']) == 1){
			$day = "0" . $today['mday'];
		}
		else{
			$day = $today['mday'];
		}
		$filename = "/home/pi/smokerController/smokerData/smokerData_" . $today['year'] . "-" . $month . "-" . $day . ".txt"; 

		$contents = file($filename);
		foreach($contents as $line) {
			$line_split = explode(",", $line);
			if ( is_numeric($line_split[0]) ){
				echo $line_split[0] . "/" . $line_split[1] . "/";
			}
		}
	}
	else{
		$today = getdate();
		if (strlen($today['mon']) == 1){
			$month = "0" . $today['mon'];
		}
		else{
			$month = $today['mon'];
		}
		if (strlen($today['mday']) == 1){
			$day = "0" . $today['mday'];
		}
		else{
			$day = $today['mday'];
		}
		$file = "/home/pi/smokerController/smokerData/smokerData_" . $today['year'] . "-" . $month . "-" . $day . ".txt"; 
		$data = file($file);
		$line = $data[count($data)-1];
		echo $line;
	}
?>