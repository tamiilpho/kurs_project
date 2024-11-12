import sqlite3

def initialize_db():
    conn = sqlite3.connect('DB/store.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sex TEXT NOT NULL,
            brand TEXT NOT NULL,
            season TEXT NOT NULL,
            price REAL NOT NULL,
            discount_price REAL,
            article TEXT UNIQUE NOT NULL,
            colors TEXT,
            sizes TEXT,
            image_path TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            favorites TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_nickname TEXT NOT NULL,
            product_name TEXT NOT NULL,
            product_article TEXT NOT NULL,
            order_time TEXT NOT NULL,
            amount_due REAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


def get_user(telegram_id):
    conn = sqlite3.connect('DB/store.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users WHERE telegram_id = ?
    ''', (telegram_id,))

    user = cursor.fetchone()
    conn.close()

    if user:
        user_dict = {
            "id": user[0],
            "telegram_id": user[1],
            "username": user[2],
            "role": user[3],
            "favorites": user[4]
        }
        return user_dict
    return None

def add_user(telegram_id, username, role):
    conn = sqlite3.connect('DB/store.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (telegram_id, username, role)
        VALUES (?, ?, ?)
    ''', (telegram_id, username, role))
    conn.commit()
    conn.close()


def add_product(name, sex, brand, season, price, discount_price, article, colors, sizes, image_path):
    conn = sqlite3.connect('DB/store.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO products (name, sex, brand, season, price, discount_price, article, colors, sizes, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, sex, brand, season, price, discount_price, article, colors, sizes, image_path))

    conn.commit()
    conn.close()


def get_product_by_article(article):
    conn = sqlite3.connect('DB/store.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM products WHERE article = ?
    ''', (article,))

    product = cursor.fetchone()
    conn.close()

    if product:
        return {
            'id': product[0],
            'name': product[1],
            'sex': product[2],
            'brand': product[3],
            'season': product[4],
            'price': product[5],
            'discount_price': product[6],
            'article': product[7],
            'colors': product[8],
            'sizes': product[9],
            'image_path': product[10]
        }
    else:
        return None


def search_products_for_user(sex, brand, size):
    conn = sqlite3.connect('DB/store.db')
    cursor = conn.cursor()

    brand = brand.lower()
    size = size.lower()

    query = """
        SELECT * FROM products
        WHERE (LOWER(sex) = LOWER(?) OR LOWER(sex) = 'unisex')
        AND LOWER(brand) = LOWER(?)
        AND LOWER(sizes) LIKE LOWER(?)
    """

    size_wildcard = f"%{size}%"
    cursor.execute(query, (sex, brand, size_wildcard))

    products = cursor.fetchall()
    conn.close()

    product_list = []
    for product in products:
        product_list.append({
            'id': product[0],
            'name': product[1],
            'sex': product[2],
            'brand': product[3],
            'season': product[4],
            'price': product[5],
            'discount_price': product[6],
            'article': product[7],
            'colors': product[8],
            'sizes': product[9],
            'image_path': product[10],
        })

    return product_list


def get_product_by_id(product_id):
    conn = sqlite3.connect('DB/store.db')
    cursor = conn.cursor()

    query = """
        SELECT * FROM products
        WHERE id = ?
    """

    cursor.execute(query, (product_id,))

    product = cursor.fetchone()
    conn.close()

    if product:
        return {
            'id': product[0],
            'name': product[1],
            'sex': product[2],
            'brand': product[3],
            'season': product[4],
            'price': product[5],
            'discount_price': product[6],
            'article': product[7],
            'colors': product[8],
            'sizes': product[9],
            'image_path': product[10],
        }

    return None


def remove_product_by_article(article):
    connection = sqlite3.connect('DB/store.db')
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM products WHERE article = ?", (article,))
        connection.commit()
        if cursor.rowcount > 0:
            return True
        else:
            return False
    except sqlite3.Error as e:
        print(f"Ошибка при удалении товара: {e}")
        return False
    finally:
        cursor.close()
        connection.close()


def add_to_favorites(user_id, product_article):
    conn = sqlite3.connect('DB/store.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT favorites FROM users WHERE telegram_id = ?', (user_id,))
        result = cursor.fetchone()

        if result:
            favorites = result[0]
            if favorites:
                favorites_list = favorites.split(',')
            else:
                favorites_list = []

            if product_article not in favorites_list:
                favorites_list.append(product_article)

            new_favorites = ','.join(favorites_list)
            cursor.execute('UPDATE users SET favorites = ? WHERE telegram_id = ?', (new_favorites, user_id))
        else:
            cursor.execute('INSERT INTO users (telegram_id, username, role, favorites) VALUES (?, ?, ?, ?)',
                           (user_id, 'username_placeholder', 'customer', product_article))

        conn.commit()
    except Exception as e:
        print(f"Ошибка при добавлении в избранное: {e}")
    finally:
        conn.close()


def get_user_favorites(user_id):
    conn = sqlite3.connect('DB/store.db')
    cursor = conn.cursor()

    cursor.execute('SELECT favorites FROM users WHERE telegram_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result and result[0]:
        return result[0].split(',')
    return []


def save_order_to_db(order):
    conn = sqlite3.connect('DB/store.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (customer_nickname, product_name, product_article, order_time, amount_due)
        VALUES (?, ?, ?, ?, ?)
    ''', (order.customer_nickname, order.product_name, order.product_article, order.order_time, order.amount_due))
    conn.commit()
    conn.close()


def get_all_orders():
    conn = sqlite3.connect('DB/store.db')
    cursor = conn.cursor()

    query = "SELECT * FROM orders"
    cursor.execute(query)

    orders = cursor.fetchall()
    conn.close()

    order_list = []
    for order in orders:
        order_list.append({
            'order_id': order[0],
            'customer_nickname': order[1],
            'product_name': order[2],
            'product_article': order[3],
            'timestamp': order[4],
            'amount_due': order[5]
        })

    return order_list


def mark_order_as_processed(order_id):
    conn = sqlite3.connect('DB/store.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            DELETE FROM orders
            WHERE id = ?
        ''', (order_id,))

        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Ошибка при удалении заказа: {e}")
        return False
    finally:
        conn.close()
