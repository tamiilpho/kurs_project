import datetime


class Order:
    def __init__(self, order_id, customer_nickname, product_name, product_article, order_time, amount_due):
        self.order_id = order_id
        self.customer_nickname = customer_nickname
        self.product_name = product_name
        self.product_article = product_article
        self.order_time = order_time
        self.amount_due = amount_due

    def __str__(self):
        return (f"Order ID: {self.order_id}\n"
                f"Customer Nickname: {self.customer_nickname}\n"
                f"Product Name: {self.product_name}\n"
                f"Product Article: {self.product_article}\n"
                f"Order Time: {self.order_time.strftime('%Y-%m-%d %H:%M:%S')}")
