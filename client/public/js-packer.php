#!/usr/bin/env php
<?php

require(dirname(__FILE__).'/class.JavaScriptPacker.php');

$dir = realpath(dirname(__FILE__).'/../').'/';
$out = 'jsocket.js';

$files = array(
	'jsocket.min.js',
	'lib/json.js',
	'core/jsocketCoreTCP.js',
	'core/jsocketCoreHTTP.js',
	'core/jsocketApi.js',
	'core/jsocketFlash.js',
);
$src = array();

foreach ($files as $key => $file) {
	$src[] = file_get_contents($dir.$file);
}

$packer = new JavaScriptPacker(implode(chr(10), $src));
$script = $packer->pack();

file_put_contents($out, $script);
