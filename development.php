<?php
    function d($variable) {
        echo '<pre>';
        var_dump($variable);
        echo '</pre>';
    }

    function dd($variable) {
        d($variable);
        exit;
    }
?>