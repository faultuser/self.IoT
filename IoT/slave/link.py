# =============================================================================
# Author: falseuser
# File Name: link.py
# Created Time: 2018-08-29 16:38:37
# Last modified: 2018-09-08 16:27:46
# Description:
# =============================================================================
import paho.mqtt.client as mqtt
# from configure import CONFIG
from slave_utils import link_logger, slave_logger, config


class SlaveLink(object):

    def __init__(self, client_id, parent_topic):
        self.client_id = client_id
        self.data_topic = "{0}/{1}/data".format(parent_topic, client_id)
        self.cmd_topic = "{0}/{1}/cmd".format(parent_topic, client_id)
        self.status_id = 255
        self.status_msg = ""
        self.userdata = ""
        self.config_link()

    def config_link(self):
        self.client = mqtt.Client(client_id=self.client_id)
        if config.getboolean("mqtt", "use_tls"):
            self.client.tls_set(
                ca_certs=config.get("mqtt", "tls_ca_file"),
                certfile=config.get("mqtt", "tls_cert_file"),
                keyfile=config.get("mqtt", "tls_key_file"),
            )
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        # self.client.on_publish = self.on_publish
        self.client.enable_logger(link_logger)
        self.client.connect(
            host=config.get("mqtt", "broker_host"),
            port=config.getint("mqtt", "broker_port"),
            keepalive=config.getint("mqtt", "keepalive"),
        )

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe(
            topic=self.get_topic,
            qos=2,
        )
        self.status_id = rc
        if self.status_id == 0:
            slave_logger.info("Connection success.")

    def on_message(self, client, userdata, msg):
        self.processing(msg.payload)

    def on_publish(self, client, userdata, mid):
        pass

    def send(self, payload):
        cmd_info = self.client.publish(
            topic=self.put_topic,
            payload=payload,
            qos=2,
        )
        self.last_mid = cmd_info.mid
        if cmd_info.rc != 0:
            self.status_id = cmd_info.rc
            slave_logger.warning("Link channel is broken")

    def processing(self, payload):
        # This function should implement in subclass.
        raise NotImplementedError

    def start(self):
        return self.client.loop_start()

    def stop(self):
        return self.client.loop_stop()

    def keep(self):
        return self.client.loop_forever()