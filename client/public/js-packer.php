#!/usr/bin/env php
<?php

require(dirname(__FILE__).'/class.JavaScriptPacker.php');

$dir = realpath(dirname(__FILE__).'/../').'/';
$out = 'jsocket.js';

$files = array(
	'code/jsocket.min.js',
	'lib/json2.js',
	'code/protocol.js',
	'code/core/tcp.js',
	'code/core/http.js',
	'code/core/websocket.js',
	'code/api.js',
	'code/flash.js'
);
$src = array();

foreach ($files as $key => $file) {
	$src[] = file_get_contents($dir.$file);
}

$packer = new JavaScriptPacker(implode(chr(10), $src));
$script = $packer->pack();

file_put_contents($out, $script);
