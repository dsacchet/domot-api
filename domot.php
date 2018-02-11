<?php

function getMaisonVmcMode($params) {
	$_result=exec('/usr/bin/python /var/www/handlers/airflow_get.py');
	echo $_result;
}

function putMaisonVmcMode($params) {
	$_conversion_table=array('low' => 0,'boost' => 1, 'bypass' => 2);
	if(!array_key_exists('mode',$params) || array_key_exists($params['mode'],$_conversion_table) === FALSE) {
		http_response_code(422);
		exit;
	}
	$_result=exec('/usr/bin/python /var/www/handlers/airflow_set.py '.$_conversion_table[$params['mode']]);
	header('Content-Type: application/json');
	echo '{ "command" : "putMaisonVmcMode", "result" : "'.$_result.'" }';
}


$_request_headers=apache_request_headers();

$_route=strtolower($_SERVER['REQUEST_METHOD']).preg_replace_callback('/\/([a-z])/',function($matches) {return strtoupper($matches[1]);},$_SERVER['SCRIPT_URL']);

$_decoded_data=NULL;
if($_SERVER['REQUEST_METHOD'] === 'PUT' || $_SERVER['REQUEST_METHOD'] == 'POST') {
	if(
		!array_key_exists('Content-Type',$_request_headers) ||
		strpos($_request_headers['Content-Type'],'application/json') !== 0
	) {
		http_response_code(400);
		exit;
	}
	$_raw_data = file_get_contents('php://input');
	$_decoded_data = json_decode($_raw_data,TRUE);
	if($_decoded_data === NULL) {
		http_response_code(400);
		exit;
	}
}

if(function_exists($_route)) {
	call_user_func($_route,$_decoded_data);
} else {
	http_response_code(501);
	exit;
}

?>
