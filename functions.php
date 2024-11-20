<?php
    /**
     * The `Functions` class extends the `Database` class and provides various operations related to products.
     */
    class Functions extends Database {

        /**
         * Fetches all products from the `products` table.
         * @return array List of all products.
         * 
         * JSON Input: None required.
         */
        public function getAllProducts() {
            return Database::query('SELECT * FROM products', 1);
        }

        /**
         * Fetches products by name from the `products` table using a search query.
         * @return array|string List of matching products or an error message.
         * 
         * JSON Input Example: { "name": "Product Name" }
         */
        public function getProductsByName() {
            if(isset($_POST['name']) && $_POST['name'] != '') {
                return Database::query("SELECT * FROM products WHERE productName LIKE '%" . $_POST['name'] . "%'", 1);
            }
            else {
                return '$_POST variable "name" was empty';
            }
        }

        /**
         * Fetches a single product by ID from the `products` table.
         * @return array|string Details of the product or an error message.
         * 
         * JSON Input: Pass the `id` as a GET parameter.
         * Example: ?id=1
         */
        public function getProductById() {
            if(isset($_GET['id']) && $_GET['id'] != '') {
                return Database::query("SELECT * FROM products WHERE id=" . $_GET['id'], 1);
            }
            else {
                return '$_GET variable "id" was empty';
            }
        }

        /**
         * Fetches products based on a tag name by querying multiple related tables.
         * @return array|string List of products or an error message.
         * 
         * JSON Input Example: { "name": "Tag Name" }
         */
        public function getProductsByTagName() {
            if(isset($_POST['name']) && $_POST['name'] != '') {
                $result = Database::query("SELECT * FROM filtertags WHERE name LIKE '" . $_POST['name'] . "'", 1);
                if(!empty($result)) {
                    $tagId = $result[0]['id'];

                    $result = Database::query("SELECT `products_id` FROM products_filtertags_junction WHERE filterTags_id=" . $tagId, 1);
                    if(!empty($result)) {
                        $productIds = $result;

                        $products = [];
                        foreach($productIds as $productId) {
                            $products[] = Database::query("SELECT * FROM products WHERE id=" . $productId['products_id'], 1);
                        }
                        return $products;
                    }
                    else {
                        return 'No results found';
                    }
                }
                else {
                    return 'No results found';
                }
            }
            else {
                return '$_POST variable "name" was empty';
            }
        }

        /**
         * Updates a product's information in the `products` table.
         * @return string Query result or an error message.
         * 
         * JSON Input Example:
         * GET: ?id=1
         * POST: { "productName": "New Name", "description": "New Description", "sku": "12345" }
         */
        public function editProduct() {
            if(isset($_GET['id']) && $_GET['id'] != '') {
                if(!empty($_POST)) {
                    $issetList = ['productName', 'description', 'sku'];
                    $checkedList = [];

                    foreach($issetList as $i) {
                        if(isset($_POST[$i]) && $_POST[$i] != '') {
                            $checkedList[] = $i;
                        }
                    }
                    
                    $updates = '';
                    foreach($checkedList as $key => $i) {
                        $addComma = ($key+1 != count($checkedList)) ? ',' : '';
                        $updates .= $i . '="' . $_POST[$i] . '"' . $addComma;
                    }

                    $sql = "UPDATE products SET " .
                        $updates . 
                        " WHERE id=" . $_GET['id'];
                    
                    return Database::query($sql);
                }
            }
            else {
                return 'No id was given';
            }
        }

        /**
         * Updates stock value for a product in the `supplies` table.
         * @return string Query result or an error message.
         * 
         * JSON Input Example:
         * GET: ?productsId=1&stock=100
         */
        public function editStock() {
            if((isset($_GET['productsId']) && $_GET['productsId'] != '')
                && (isset($_GET['stock']) && $_GET['stock'] != '')) {
                    $sql = "UPDATE supplies SET 
                            products_id=" . $_GET['productsId'] . ", value=" . $_GET['stock'];

                    return Database::query($sql);
            }
            else {
                return 'No productsId or stock given';
            }

        }

        /**
         * Creates a new product and initializes its stock.
         * @return string Query result or an error message.
         * 
         * JSON Input Example:
         * POST: { "productName": "Product Name", "description": "Description", "sku": "12345", "amountOfStock": 100 }
         */
        public function createProduct() {
            $issetList = ['productName', 'description', 'sku', 'amountOfStock'];
            foreach($issetList as $i) {
                if(isset($_POST[$i]) && $_POST[$i] != '') {
                    $checkedList[] = $i;
                }
                else {
                    return $i . " was not set";
                }
            }
            
            $sql = "INSERT INTO products (`productName`, `description`, `sku`) VALUES ('" . 
                $_POST['productName'] . "', '" . $_POST['description'] . "', '" . $_POST['sku'] . "')";

            Database::query($sql);

            $sql2 = "INSERT INTO supplies (`products_id`, `value`) VALUES (" . 
                $this->conn->insert_id . ", " . $_POST['amountOfStock'] . ")";
            
            return Database::query($sql2);
        }
    }
?>
