from configparser import ConfigParser
import logging
import sys
import sqlite3

CONSTANTS = ConfigParser()
CONSTANTS.read("../constants.ini")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def connect(db_filepath) -> tuple:
    conn = sqlite3.connect(db_filepath)
    cursor = conn.cursor()
    return conn, cursor


def insert_new_customer(user_id: int, username: str, first_name: str, last_name: str) -> None:
    """Stuff"""
    logger.info("insert_new_customer()")
    conn, cursor = connect(CONSTANTS.get("ORDER_DISPATCHER_BOT", "DATABASE_FILEPATH"))
    result = cursor.execute("select * from Customers where CustomerID = ?", (user_id,))
    if result.fetchone() is None:
        cursor.execute("insert into Customers (CustomerID, UserName, FirstName, LastName) values (?, ?, ?, ?);",
                       (user_id, username, first_name, last_name))
        conn.commit()
    else:
        logger.info("Customer already in Database")


def insert_customer_phone_number(user_id: int, phone_number: int) -> None:
    logger.info("insert_customer_phone_number()")
    conn, cursor = connect(CONSTANTS.get("ORDER_DISPATCHER_BOT", "DATABASE_FILEPATH"))
    result = cursor.execute("select * from Customers where CustomerID = ?", (user_id,))
    if result.fetchone() is not None:
        cursor.execute("update Customers set PhoneNumber = ? where CustomerID = ?;",
                       (phone_number, user_id))
        conn.commit()
        logger.info("Phone number added into Database")
    else:
        logger.info("Customer not in Database")


def get_customer_data(user_id: int) -> list:
    logger.info("get_customer_data()")
    conn, cursor = connect(CONSTANTS.get("ORDER_DISPATCHER_BOT", "DATABASE_FILEPATH"))
    result = cursor.execute("select * from Customers where CustomerID = ?", (user_id,))

    return result.fetchone()


def insert_new_order(user_id: int, device_context: dict, default_contractor_id: int = int(CONSTANTS.get("TELEGRAM_ID", "USER_ID_FR"))) -> None:
    logger.info("insert_new_order()")
    conn, cursor = connect(CONSTANTS.get("ORDER_DISPATCHER_BOT", "DATABASE_FILEPATH"))
    cursor.execute("insert into Orders (CustomerID, ContractorID, Device_OS, Device, Part, Problem) "
                   "values (?, ?, ?, ?, ?, ?);",
                   (user_id, default_contractor_id,
                    device_context["Device_OS_Brand"], device_context["Device"],
                    device_context["Part"], device_context["Problem"]))
    conn.commit()


def get_order_data(OrderID: int) -> list:
    logger.info("get_order_data()")
    conn, cursor = connect(CONSTANTS.get("ORDER_DISPATCHER_BOT", "DATABASE_FILEPATH"))
    result = cursor.execute("select * from Orders where OrderID = ?", (OrderID,))

    return result.fetchone()


def get_customer_last_OrderID(user_id: int, default_contractor_id: int = int(CONSTANTS.get("TELEGRAM_ID", "USER_ID_FR"))) -> int:
    logger.info("get_customer_last_OrderID()")
    conn, cursor = connect(CONSTANTS.get("ORDER_DISPATCHER_BOT", "DATABASE_FILEPATH"))
    result = cursor.execute("select * from Orders where (CustomerID = ? and ContractorID = ?)",
                            (user_id, default_contractor_id))
    orders = result.fetchall()

    return orders[-1][0]


def get_contractor_data(user_id: int) -> list:
    logger.info("get_contractor_data()")
    conn, cursor = connect(CONSTANTS.get("ORDER_DISPATCHER_BOT", "DATABASE_FILEPATH"))
    result = cursor.execute("select * from Contractors where ContractorID = ?", (user_id,))

    return result.fetchone()


def update_order_ContractID(OrderID: int, new_ContractorID: int):
    logger.info("update_order_ContractID()")
    conn, cursor = connect(CONSTANTS.get("ORDER_DISPATCHER_BOT", "DATABASE_FILEPATH"))
    cursor.execute("update Orders set ContractorID = ? where OrderID = ?;",
                   (new_ContractorID, OrderID))
    conn.commit()
