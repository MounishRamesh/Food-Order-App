import mysql.connector
import pandas as pd
from datetime import datetime


def create_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='ramesh@05"',
        database='foods'
    )


def run_queries_and_save():
    queries = {
        "1_Total_Revenue": """
            SELECT SUM(oi.price * oi.quantity) AS total_revenue
            FROM order_items oi;
        """,

        "2_Revenue_By_Item": """
            SELECT i.item_name, SUM(oi.price * oi.quantity) AS total_revenue
            FROM order_items oi 
            JOIN items i ON oi.item_id = i.item_id
            GROUP BY i.item_name
            ORDER BY total_revenue DESC;
        """,

        "3_Revenue_By_Payment_Method": """
            SELECT p.payment_method, SUM(p.amount) AS total_revenue
            FROM payments p 
            JOIN orders o ON p.order_id = o.order_id
            GROUP BY p.payment_method;
        """,

        "4_Total_Revenue_By_Date": """
            SELECT DATE(p.paid_at) AS date, SUM(p.amount) AS daily_revenue
            FROM payments p
            GROUP BY DATE(p.paid_at)
            ORDER BY date;
        """,

        "5_Total_Orders_And_Revenue_By_User": """
            SELECT
                c.first_name,
                c.last_name,
                c.phone_number,
                c.email,
                COUNT(o.order_id) AS total_orders,
                SUM(oi.price * oi.quantity) AS total_revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN customers c ON o.user_id = c.user_id
            GROUP BY c.user_id
            ORDER BY total_revenue DESC;
        """,

        # "6_Items_Ordered_By_Category": """
        #     SELECT c.category_name, i.item_name, SUM(oi.quantity) AS total_quantity_ordered
        #     FROM order_items oi
        #     JOIN items i ON oi.item_id = i.item_id
        #     JOIN categories c ON i.category_id = c.category_id
        #     GROUP BY c.category_name, i.item_name
        #     ORDER BY total_quantity_ordered DESC;
        # """,

        "7_Orders_By_Payment_Status": """
            SELECT p.payment_status, COUNT(o.order_id) AS total_orders
            FROM payments p
            JOIN orders o ON p.order_id = o.order_id
            GROUP BY p.payment_status;
        """,

        "8_Users_With_Most_Orders": """
            SELECT
                c.first_name,
                c.last_name,
                COUNT(o.order_id) AS total_orders
            FROM customers c
            JOIN orders o ON c.user_id = o.user_id
            GROUP BY c.user_id
            ORDER BY total_orders DESC
            LIMIT 5;
        """,

        # "9_Revenue_By_Category": """
        #     SELECT c.category_name, SUM(oi.price * oi.quantity) AS total_revenue
        #     FROM order_items oi
        #     JOIN items i ON oi.item_id = i.item_id
        #     JOIN categories c ON i.category_id = c.category_id
        #     GROUP BY c.category_name;
        # """,

        "10_Items_Purchased_In_Specific_Order": """
            SELECT oi.order_id, i.item_name, oi.quantity, oi.price
            FROM order_items oi
            JOIN items i ON oi.item_id = i.item_id
            WHERE oi.order_id = 1;
        """,

        "11_Customer_Details_With_Orders": """
            SELECT
                c.first_name,
                c.last_name,
                c.phone_number,
                c.email,
                o.order_id,
                o.delivery_address,
                oi.item_id,
                oi.quantity
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN customers c ON o.user_id = c.user_id;
        """,

        "12_Revenue_By_Customer": """
            SELECT
                c.first_name,
                c.last_name,
                c.phone_number,
                c.email,
                SUM(oi.price * oi.quantity) AS total_revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN customers c ON o.user_id = c.user_id
            GROUP BY c.user_id
            ORDER BY total_revenue DESC;
        """
    }

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Use 'with' to properly save all sheets
    with pd.ExcelWriter(f'daily_report_{now}.xlsx', engine='openpyxl') as writer:
        for name, query in queries.items():
            print(f"Running: {name} ...")
            cursor.execute(query)
            data = cursor.fetchall()
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=name[:30], index=False)
            print(f"saved: {name}")

    cursor.close()
    connection.close()
    print("\n🎉 All 12 reports generated successfully in Excel!")


if __name__ == "__main__":
    run_queries_and_save()

