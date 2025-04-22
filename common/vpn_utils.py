import os

from dotenv import find_dotenv, load_dotenv
from py3xui import Inbound

load_dotenv(find_dotenv())

SERVER_PORT = os.getenv("PORT")
XUI_EXTERNAL_IP = os.getenv("XUI_EXTERNAL_IP")
MAIN_REMARK = os.getenv("MAIN_REMARK")
XUI_EXTERNAL_URL = os.getenv("XUI_EXTERNAL_URL")


def get_connetion_string(inbound: Inbound, user_uuid: str, name: str) -> str:
    public_key = inbound.stream_settings.reality_settings.get("settings").get("publicKey")
    website_name = inbound.stream_settings.reality_settings.get("serverNames")[0]
    short_id = inbound.stream_settings.reality_settings.get("shortIds")[0]

    connection_string = (
        f"vless://{user_uuid}@{XUI_EXTERNAL_URL}:{SERVER_PORT}"
        f"?type=tcp&security=reality&pbk={public_key}&fp=firefox&sni={website_name}"
        f"&sid={short_id}&spx=%2F&flow=xtls-rprx-vision#{MAIN_REMARK}-{name}"
    )

    return connection_string


