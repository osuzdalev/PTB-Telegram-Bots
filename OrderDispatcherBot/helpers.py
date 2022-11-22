from configparser import ConfigParser
import logging
from pprint import pformat
import sys

CONSTANTS = ConfigParser()
CONSTANTS.read("../constants.ini")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def get_order_message_str(OrderID: int, user_data: any, device_context: any, phone_number: int = None) -> str:
    """Creates a nice string with all the relevant data of an Order to be sent as a message to Contractor"""
    logger.info("get_order_message_str()")
    user_info = ""
    if type(user_data) == list:
        user_info = user_data[1] + '\n' + \
                    user_data[2] + '\n' + user_data[3] + '\n' + str(phone_number) + '\n' + \
                    "id:" + str(user_data[0])
    elif type(user_data) == tuple:
        user_info = '@' + user_data[1] + '\n' + \
                    user_data[2] + '\n' + user_data[3] + '\n' + str(phone_number) + '\n' + \
                    "id:" + str(user_data[0])

    device_info = ""
    logger.info("device_context: {}".format(device_context))
    if type(device_context) == dict:
        if device_context == {"Device_OS_Brand": '', "Device": '', "Part": '', "Problem": ''}:
            device_info = "Device_OS: " + "-" + '\n' + \
                          "Device: " + "-" + '\n' + \
                          "Part: " + "-" + '\n' + \
                          "Problem: " + "-"
        else:
            device_info = "Device_OS: " + device_context["Device_OS_Brand"] + '\n' + \
                          "Device: " + device_context["Device"] + '\n' + \
                          "Part: " + device_context["Part"] + '\n' + \
                          "Problem: " + device_context["Problem"]
    elif type(device_context) == tuple:
        device_info = "Device_OS: " + device_context[4] + '\n' + \
                      "Device: " + device_context[5] + '\n' + \
                      "Part: " + device_context[6] + '\n' + \
                      "Problem: " + device_context[7]

    order_message_str = "Customer service required\n\n" \
                        "Order# {}\n\n{}\n\n{}".format(str(OrderID), user_info, device_info)

    return order_message_str
