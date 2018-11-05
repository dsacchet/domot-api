<?php


function notifSms($params) {

	include($_SERVER['DOCUMENT_ROOT'].'/../conf/notif/sms/orange.php');

	/* STEP 1 : Initialize cookie */
	error_log('curl init cookie with https://id.orange.fr/auth_user/bin/auth_user.cgi');
	$cookie_file=tempnam($_SERVER['DOCUMENT_ROOT'].'/../run/','domot_cookie_notif_');
	error_log('cookie file : '.$cookie_file);
	$ch=curl_init('https://id.orange.fr/auth_user/bin/auth_user.cgi');
	curl_setopt($ch, CURLOPT_COOKIEJAR, $cookie_file);
	curl_setopt($ch, CURLOPT_COOKIEFILE, $cookie_file);
	curl_setopt($ch, CURLOPT_USERAGENT, 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0');
	curl_setopt($ch, CURLOPT_TIMEOUT, 60); 
	curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 0);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($ch, CURLOPT_HEADER, 0);
	curl_setopt($ch, CURLINFO_HEADER_OUT, 0);
	curl_setopt($ch, CURLOPT_VERBOSE, 0);
	$result=curl_exec($ch);
	curl_close($ch);

	/* STEP 2 : Login */
	error_log('curl login with https://id.orange.fr/auth_user/bin/auth_user.cgi');
	$ch=curl_init('https://id.orange.fr/auth_user/bin/auth_user.cgi');
	$fields_string='';
	$fields=array(
		'credential'=>urlencode($notifSmsOrangeUsername),
		'password'=>urlencode($notifSmsOrangePassword)
	);
	foreach($fields as $key=>$value) { $fields_string .= $key.'='.$value.'&'; }
	rtrim($fields_string, '&');
	curl_setopt($ch, CURLOPT_POST, count($fields));
	curl_setopt($ch, CURLOPT_POSTFIELDS, $fields_string);
	curl_setopt($ch, CURLOPT_COOKIEJAR, $cookie_file);
	curl_setopt($ch, CURLOPT_COOKIEFILE, $cookie_file);
	curl_setopt($ch, CURLOPT_USERAGENT, 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0');
	curl_setopt($ch, CURLOPT_TIMEOUT, 60); 
	curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 0);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($ch, CURLOPT_HEADER, 0);
	curl_setopt($ch, CURLINFO_HEADER_OUT, 0);
	curl_setopt($ch, CURLOPT_VERBOSE, 0);
	$result=curl_exec($ch);
	error_log('curl login result : '.$result);
	curl_close($ch);

	/* STEP 3 : Send SMS */
	error_log('curl sendsms with https://smsmms.orange.fr/api/v1/messages');
	$ch=curl_init('https://smsmms.orange.fr/api/v1/messages');
	curl_setopt($ch, CURLOPT_COOKIEJAR, $cookie_file);
	curl_setopt($ch, CURLOPT_COOKIEFILE, $cookie_file);
	curl_setopt($ch, CURLOPT_USERAGENT, 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0');
	curl_setopt($ch, CURLOPT_TIMEOUT, 60); 
	curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 0);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($ch, CURLOPT_HEADER, 0);
	curl_setopt($ch, CURLINFO_HEADER_OUT, 0);
	curl_setopt($ch, CURLOPT_VERBOSE, 0);
	curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
	foreach ($params['recipients'] as $recipient) {
		$data=array(
			"type" => "xms",
			"messageId" => 0,
			"content" => $params['message'],
			"replyType" => "on_mobile",
			"recipients" => array($recipient),
			"attachments" => array(),
			"mmsData" => ""
		);
		$data_string=json_encode($data);
		echo "data string : ".$data_string."\n";
		curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);
		curl_setopt($ch, CURLOPT_REFERER, 'https://smsmms.orange.fr');
		curl_setopt($ch, CURLOPT_HTTPHEADER, array(
			'Content-Type: application/json',
			'Content-Length: ' . strlen($data_string))
		);
		$result=curl_exec($ch);
		error_log('curl sendsms result : '.$result);
	}
	curl_close($ch);
//unlink($cookie_file);
}
