This project aims to implement a Smart Supermarket concept to improve the management of the retail industry by incorporating Internet of Things (IoT) technologies. It focuses on transforming traditional supermarkets into "smart" supermarkets through the development of an automation application for better management of retail shops in the food industry and optimizing store operations. In particular, we developed two kinds of sensors:

1. **Smart Shelves**
2. **Smart Fridges**

---

![SmartShelves](https://github.com/enricollen/IoT_Smart_Supermarket/blob/master/img/smart_shelf.jpg?raw=true)

## 🛒 Smart Shelves [CoAP]
- **Sensors**: Weight sensors
- **Actuators**: Price Displays

### ⚖️ Weight Sensors
- **Logic**: Periodically measure weight and update inventory status.
- **Endpoints**: Expose resources for weight measurement and shelf refill status.
- **Communication**: Use CoAP for sending data to the collector.

### 💲 Price Displays
- **Logic**: Display and update product prices.
- **Endpoints**: Expose resources for price updates.
- **Communication**: Use CoAP for receiving price updates from the collector.

Smart shelves are composed of two different devices, the weight sensor to measure the weight of products on the shelf to monitor inventory levels and the price display to show the current price of the products. They were designed to automatically keep track of inventory in any retail establishment (in our case, supermarkets). With smart shelves, supermarket owners can collect real-time data about their products. The shelves are able to gather information about which products have or haven't been bought, and in which period of time. Business owners are therefore more informed about product selling ratios and buying trends, enabling them to better supply their stores.

In addition, Smart shelves can optimize in-store operations like alerting employees to low inventory, allowing them to restock shelves promptly. They can also schedule coupons and discounts based on selling ratios, all done automatically. This automation allows personnel to focus more on customer needs, improving team management by giving them more time to complete other tasks.

These devices communicate using the **CoAP** (Constrained Application Protocol) and are managed by a control logic implemented in a collector.

---

![SmartFridges](https://github.com/enricollen/IoT_Smart_Supermarket/blob/master/img/smart_fridge.jpg?raw=true)

## 🥶 Smart Fridges [MQTT]
- **Sensors**: Temperature sensors
- **Actuators**: Remote Alarm

### 🌡️ Temperature Sensors
- **Logic**: Monitor and report the temperature; adjust compressor state.
- **Endpoints**: Publish temperature data and subscribe to desired temperature settings.
- **Communication**: Use MQTT for data transmission.

### 🚨 Remote Light Alarms
- **Logic**: Indicate alarms based on temperature readings.
- **Endpoints**: Publish alarm states and subscribe to alarm control commands.
- **Communication**: Use MQTT for receiving commands and updating alarm states.

The Smart Fridge is composed of two devices as well, the temperature sensor for monitoring the fridge's internal temperature and the remote light alarm to indicate issues like temperature deviations. The aim was to monitor refrigerator temperature to increase energy savings and avoid long periods of opened doors caused by people's negligence.

These devices use MQTT (Message Queuing Telemetry Transport) for communication and are controlled by a central collector.

---

# 🏗️ System Architecture
![Architecture](https://github.com/enricollen/IoT_Smart_Supermarket/blob/master/img/architecture.jpg?raw=true)
We implemented the nodes’ firmware using Contiki-NG as the operating system, and using a simulation environment with Cooja. The nodes that we used to deploy our system on are NRF52840.

## 🗃️ Collector
The collector, written in Python, manages communication with CoAP and MQTT devices, stores data in a MySQL database, and provides a CLI for user interaction. It also handles node registration, data storage, and command execution.
![Collector](https://github.com/enricollen/IoT_Smart_Supermarket/blob/master/img/collector.jpg?raw=true)

## 🗄️ Data Storage
Data from the IoT devices is stored in a MySQL database by the Collector.
