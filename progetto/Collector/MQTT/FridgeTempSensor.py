from MQTT.MqttClient import MqttClient



class FridgeTempSensor(MqttClient):

    node_id = ""
    pub_topic = ""

    def __init__(self, node_id):
        self.node_id = node_id
        sub_topic = "fridge/" + self.node_id + "/temperature"
        self.pub_topic = "fridge/"+ self.node_id + "/desired_temp"
        super().__init__(sub_topic)

    def change_setpoint(self, new_setpoint):
        return

    def on_message(self, client, userdata, msg):
        #TO DO:
        #should parse state from json and update class state,
        #it should also save the received state in the database
        return