<?php
    class Database {

        protected $conn;
        public function __construct() {
            require('config.php');
            $connection = @new mysqli(
                $databaseData['host'],
                $databaseData['user'],
                $databaseData['password'],
                $databaseData['databaseName']
            );
            if($connection->connect_errno) {
                echo 'Api could\'t connect to the database';
                exit;
            }
            else {
                $this->conn = $connection;
            }
        }

        public function query(String $query = NULL, int $callback = NULL) {
            $conn = $this->conn;
            if ($conn) {
                if($query == NULL || $query == '') {
                    echo 'query was not filled in';
                    return;
                }
                $result = $conn->query($query);
                if($result) {
                    if($callback !== NULL && $callback !== 0) {
                        $list = [];
                        while($item = $result->fetch_assoc()) {
                            $list[] = $item;
                        }
                        return $list;
                    }
                    return $result;
                }
                echo 'Couldn\'t execute the filled in query';
                exit;
            }
            return $conn;
        }
    }
?>