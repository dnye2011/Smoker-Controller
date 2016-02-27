<?php		
	$temp = $_GET['setTemp'];
	file_put_contents( "/home/pi/smokerController/fanSetTemp.txt", $temp);
?>