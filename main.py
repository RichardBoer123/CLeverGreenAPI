import pymysql
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database connection function
def get_db_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',  # Change to your DB username
            password='root',  # Change to your DB password
            database='clevergreen',
            cursorclass=pymysql.cursors.DictCursor  # Use dictionary cursor
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to database: {e}")
        return None

# Endpoint: Get All Products
@app.route('/getAllProducts/', methods=['GET'])
def get_all_products():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    try:
        cursor = conn.cursor()
        query = "SELECT * FROM products"
        cursor.execute(query)
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(products)
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Failed to fetch products: ' + str(e)}), 500

# Endpoint: Get Product by ID
@app.route('/getProductById/', methods=['GET'])
def get_product_by_id():
    product_id = request.args.get('id')
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    try:
        cursor = conn.cursor()
        query = "SELECT * FROM products WHERE product_id = %s"
        cursor.execute(query, (product_id,))
        product = cursor.fetchone()
        cursor.close()
        conn.close()

        if product:
            return jsonify(product)
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Failed to fetch product: ' + str(e)}), 500

# Endpoint: Get Product by Name
@app.route('/getFilteredProducts', methods=['GET'])
def get_filtered_products():
    category_id = request.args.get('category', default=None, type=int)
    product_name = request.args.get('name', default="", type=str)

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    try:
        cursor = conn.cursor()

        # Start building the query
        query = "SELECT * FROM products WHERE product_name LIKE %s"
        params = ['%' + product_name + '%']  # Add name filter

        # If category is provided, add it to the query
        if category_id:
            query += " AND category_id = %s"
            params.append(category_id)

        cursor.execute(query, tuple(params))
        products = cursor.fetchall()
        cursor.close()
        conn.close()

        # If products are found, return them; else, return an empty list
        if products:
            return jsonify(products)
        else:
            return jsonify([])  # Return an empty list if no products match

    except Exception as e:
        conn.close()
        return jsonify({'error': 'Failed to fetch products: ' + str(e)}), 500




# Endpoint: Create Product
@app.route('/createProduct/', methods=['POST'])
def create_product():
    # Get the JSON data from the request
    data = request.get_json()

    # Define required fields
    required_fields = ['product_name', 'category_id', 'stock_quantity']
    
    # Check if all required fields are provided
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Extract data from request
    product_name = data['product_name']
    category_id = data['category_id']
    stock_quantity = data['stock_quantity']

    # Validate stock_quantity (ensure it's a valid non-negative number)
    if not isinstance(stock_quantity, int) or stock_quantity < 0:
        return jsonify({'error': 'Invalid stock quantity'}), 400

    # Connect to the database
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    try:
        # Check if the category exists in the categories table
        cursor = conn.cursor()
        cursor.execute("SELECT category_id FROM categories WHERE category_id = %s", (category_id,))
        category = cursor.fetchone()
        
        # If the category does not exist, return an error
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        # Insert the product into the products table
        query = "INSERT INTO products (product_name, category_id, stock_quantity) VALUES (%s, %s, %s)"
        cursor.execute(query, (product_name, category_id, stock_quantity))
        conn.commit()

        # Close the connection
        cursor.close()
        conn.close()

        # Return success message
        return jsonify({'message': 'Product created successfully'}), 201

    except Exception as e:
        # Close the connection in case of error
        conn.close()
        return jsonify({'error': 'Failed to create product: ' + str(e)}), 500


# Endpoint: Delete Product by ID
@app.route('/deleteProductById', methods=['DELETE'])
@app.route('/deleteProductById/', methods=['DELETE'])
def delete_product_by_id():
    product_id = request.args.get('id')
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    try:
        cursor = conn.cursor()

        # Check if the product exists
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # Delete the product from the products table
        delete_query = "DELETE FROM products WHERE product_id = %s"
        cursor.execute(delete_query, (product_id,))
        conn.commit()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return jsonify({'message': 'Product deleted successfully'}), 200

    except Exception as e:
        conn.close()
        return jsonify({'error': 'Failed to delete product: ' + str(e)}), 500



# Endpoint: Edit Product
@app.route('/editProduct/', methods=['PUT'])
def edit_product():
    data = request.get_json()

    # Validate the required fields (excluding 'price' since it's not in the 'products' table)
    required_fields = ['product_id', 'product_name', 'category_id', 'stock_quantity']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Extract values from the request data
    product_id = data['product_id']
    product_name = data['product_name']
    category_id = data['category_id']
    stock_quantity = data['stock_quantity']

    # Ensure stock_quantity is valid
    if not isinstance(stock_quantity, int) or stock_quantity < 0:
        return jsonify({'error': 'Invalid stock quantity'}), 400

    # Connect to the database
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    try:
        cursor = conn.cursor()

        # Check if the product exists
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # Check if the category exists
        cursor.execute("SELECT * FROM categories WHERE category_id = %s", (category_id,))
        category = cursor.fetchone()
        if not category:
            return jsonify({'error': 'Category not found'}), 404

        # Update the product in the products table (without the price)
        update_query = """
        UPDATE products
        SET product_name = %s, category_id = %s, stock_quantity = %s
        WHERE product_id = %s
        """
        cursor.execute(update_query, (product_name, category_id, stock_quantity, product_id))

        # Check if any row was actually updated
        if cursor.rowcount == 0:
            return jsonify({'error': 'No changes made to the product'}), 400

        conn.commit()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return jsonify({'message': 'Product updated successfully'}), 200

    except Exception as e:
        # Make sure to close the connection in case of error
        conn.close()
        return jsonify({'error': 'Failed to update product: ' + str(e)}), 500


# Endpoint: Create Stock Movement
@app.route('/createStockMovement/', methods=['POST'])
def create_stock_movement():
    data = request.get_json()
    required_fields = ['product_id', 'user_id', 'quantity_change', 'movement_type']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    try:
        cursor = conn.cursor()
        query = "INSERT INTO stock_movements (product_id, user_id, quantity_change, movement_type) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (data['product_id'], data['user_id'], data['quantity_change'], data['movement_type']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Stock movement created successfully'}), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Failed to create stock movement: ' + str(e)}), 500

# Endpoint: Get Stock Movements by Product ID
@app.route('/getStockMovementsByProductId/', methods=['GET'])
def get_stock_movements_by_product_id():
    product_id = request.args.get('product_id')
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    try:
        cursor = conn.cursor()
        query = "SELECT * FROM stock_movements WHERE product_id = %s"
        cursor.execute(query, (product_id,))
        movements = cursor.fetchall()
        cursor.close()
        conn.close()

        if movements:
            return jsonify(movements)
        else:
            return jsonify({'error': 'No stock movements found for this product'}), 404
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Failed to fetch stock movements: ' + str(e)}), 500
    

    # Endpoint: Get Used Categories
@app.route('/getUsedCategories/', methods=['GET'])
def get_used_categories():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Failed to connect to the database'}), 500

    try:
        cursor = conn.cursor()
        query = """
        SELECT DISTINCT c.category_id, c.category_name
        FROM categories c
        JOIN products p ON c.category_id = p.category_id
        """
        cursor.execute(query)
        categories = cursor.fetchall()
        cursor.close()
        conn.close()

        if categories:
            return jsonify(categories)
        else:
            return jsonify({'error': 'No categories found'}), 404
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Failed to fetch categories: ' + str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
