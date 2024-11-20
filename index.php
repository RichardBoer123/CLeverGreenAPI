<?php

require_once('development.php');
require_once('db.php');
require_once('functions.php');

// Make connection

// dd($conn);

-
var_dump($_GET);
$functionName = substr($_SERVER['REDIRECT_URL'], 1);
d($functionName);

if(method_exists('Functions', $functionName)) {
  echo 'success';
  $functionClass = new Functions();
  dd($functionClass->$functionName());
}
else {
    echo 'Failed';
}


// APi key check


// function check

?>