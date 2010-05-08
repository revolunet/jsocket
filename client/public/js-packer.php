#!/usr/bin/env php
<?php

require(dirname(__FILE__).'/class.JavaScriptPacker.php');

$dir = realpath(dirname(__FILE__).'/../').'/';
$out = 'jsocket.js';

$files = array(
	'jsocket.min.js',
	'lib/json2.js',
	'protocol.js',
	'core/tcp.js',
	'core/http.js',
	'api.js',
	'flash.js'
);
$src = array();

foreach ($files as $key => $file) {
	$src[] = file_get_contents($dir.$file);
}

$packer = new JavaScriptPacker(implode(chr(10), $src));
$script = $packer->pack();

file_put_contents($out, $script);
