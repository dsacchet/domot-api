<?php

function getConf($namespace,$value) {
	include($_SERVER['DOCUMENT_ROOT'].'/../conf/conf.php');
	return $$value;
}


function postMaisonMetrics($params) {
	error_reporting(E_ALL);
	error_log(serialize($params));
}

function getMaisonChaudiereConsigneJour($params) {
    $command=$_SERVER['DOCUMENT_ROOT'].'/../handlers/chaudiere/'.getConf('','chaudiere_provider').'/consigne/get jour';
	$_result=exec($command, $retArr, $retVal);
	echo '{ "route" : "',__FUNCTION__,'", "returnCode": "'.$retVal.'", "result" : '.$retArr[0].', "debug":"'.$command.'" }';
}

function putMaisonChaudiereConsigneJour($params) {
	if(array_key_exists('temperature',$params) === FALSE) {
		echo '{ "errorMessage" : "You must give a parameter temperature" }';
		http_response_code(422);
		exit;
	}
    $command=$_SERVER['DOCUMENT_ROOT'].'/../handlers/chaudiere/'.getConf('','chaudiere_provider').'/consigne/put jour '.$params['temperature'];
	$_result=exec($command,$retArr, $retVal);
	header('Content-Type: application/json');
	echo '{ "route" : "',__FUNCTION__,'", "returnCode": "'.$retVal.'", "result" : '.$retArr[0].', "debug":"'.$command.'" }';
}

function getMaisonVmcBypass($params) {
    $command=$_SERVER['DOCUMENT_ROOT'].'/../handlers/vmc/'.getConf('','vmc_provider').'/bypass/get';
	$_result=exec($command, $retArr, $retVal);
	echo '{ "route" : "',__FUNCTION__,'", "returnCode": "'.$retVal.'", "result" : '.$retArr[0].', "debug":"'.$command.'" }';
}

function putMaisonVmcBypass($params) {
	$_conversion_table=array('off' => 0,'on' => 1);
	if(!array_key_exists('bypass',$params) || array_key_exists($params['bypass'],$_conversion_table) === FALSE) {
		echo '{ "errorMessage" : "You must give in parameters a value into (off,on) to bypass variable" }';
		http_response_code(422);
		exit;
	}
	$command=$_SERVER['DOCUMENT_ROOT'].'/../handlers/vmc/'.getConf('','vmc_provider').'/bypass/put '.$_conversion_table[$params['bypass']];
    $_result=exec($command,$retArr, $retVal);
	header('Content-Type: application/json');
	echo '{ "route" : "',__FUNCTION__,'", "returnCode": "'.$retVal.'", "result" : '.$retArr[0].', "debug":"'.$command.'" }';
}

function getMaisonVmcMode($params) {
    $command=$_SERVER['DOCUMENT_ROOT'].'/../handlers/vmc/'.getConf('','vmc_provider').'/mode/get';
	$_result=exec($command, $retArr, $retVal);
	echo '{ "route" : "',__FUNCTION__,'", "returnCode": "'.$retVal.'", "result" : '.$retArr[0].', "debug":"'.$command.'" }';
}

function putMaisonVmcMode($params) {
    error_log(print_r($params,true));
	$_conversion_table=array('low' => 0,'boost' => 1, 'bypass' => 2);
	if(!array_key_exists('mode',$params) || array_key_exists($params['mode'],$_conversion_table) === FALSE) {
		echo '{ "errorMessage" : "You must give in parameters a value into (low,boost,bypass) to mode variable" }';
		http_response_code(422);
		exit;
	}
	$command=$_SERVER['DOCUMENT_ROOT'].'/../handlers/vmc/'.getConf('','vmc_provider').'/mode/put '.$_conversion_table[$params['mode']];
    $_result=exec($command,$retArr, $retVal);
	header('Content-Type: application/json');
	echo '{ "route" : "',__FUNCTION__,'", "returnCode": "'.$retVal.'", "result" : "'.$retArr[0].'", "debug":"'.$command.'" }';
}

function putMaisonNotifSms($params) {
	include($_SERVER['DOCUMENT_ROOT'].'/../handlers/notif/sms/'.getConf('','notif_sms_provider').'.php');
	notifSms($params);
}

function putMaisonNotifMail($params) {
	include($_SERVER['DOCUMENT_ROOT'].'/../handlers/notif/mail/'.getConf('','notif_mail_provider').'.php');
	notifMail($params);
}

error_reporting(E_ALL);
error_log('on y va');

$_request_headers=apache_request_headers();

error_log(serialize($_request_headers));

$_route=strtolower($_SERVER['REQUEST_METHOD']).preg_replace_callback('/\/([a-z])/',function($matches) {return strtoupper($matches[1]);},$_SERVER['SCRIPT_URL']);

error_log($_route);

$_decoded_data=NULL;
if($_SERVER['REQUEST_METHOD'] === 'PUT' || $_SERVER['REQUEST_METHOD'] == 'POST') {
	if(
		!array_key_exists('Content-Type',$_request_headers) ||
		strpos($_request_headers['Content-Type'],'application/json') !== 0
	) {
        error_log(serialize($_request_headers));
		echo '{ "errorMessage" : "Content-Type must be set to application/json" }';
		http_response_code(400);
		exit;
	}
	$_raw_data = file_get_contents('php://input');
	$_decoded_data = json_decode($_raw_data,TRUE);
	if($_decoded_data === NULL) {
        error_log("_decoded_data is NULL");
		echo '{ "errorMessage" : "Unable to decode JSON data" }';
		http_response_code(400);
		exit;
	}
    error_log(serialize($_decoded_data));
}

if(function_exists($_route)) {
	call_user_func($_route,$_decoded_data);
} else {
	echo '{ "errorMessage" : "This route is not implemented" }';
	http_response_code(501);
	exit;
}

?>
