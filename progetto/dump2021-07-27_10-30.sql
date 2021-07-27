-- MySQL dump 10.19  Distrib 10.3.29-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: smart_supermarket
-- ------------------------------------------------------
-- Server version	10.3.29-MariaDB-0ubuntu0.20.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `price_display_state`
--

DROP TABLE IF EXISTS `price_display_state`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `price_display_state` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `node_id` varchar(50) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `current_price` float NOT NULL COMMENT 'unit=euros',
  `last_price_change` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=277 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `price_display_state`
--

LOCK TABLES `price_display_state` WRITE;
/*!40000 ALTER TABLE `price_display_state` DISABLE KEYS */;
INSERT INTO `price_display_state` VALUES (236,'sciao','2021-07-26 14:47:34',20.5,'2021-07-26 14:47:22'),(237,'sciao','2021-07-26 14:54:03',20.5,'2021-07-26 14:48:36'),(238,'sciao','2021-07-26 14:54:04',20.5,'2021-07-26 14:48:36'),(239,'sciao','2021-07-26 14:54:08',20.5,'2021-07-26 14:48:35'),(240,'sciao','2021-07-26 14:54:14',20.5,'2021-07-26 14:48:36'),(241,'sciao','2021-07-26 14:58:33',20.5,'2021-07-26 14:58:21'),(242,'sciao','2021-07-26 14:58:34',20.5,'2021-07-26 14:58:20'),(243,'sciao','2021-07-26 15:00:54',20.5,'2021-07-26 15:00:42'),(244,'sciao','2021-07-26 15:00:56',20.5,'2021-07-26 15:00:42'),(245,'sciao','2021-07-26 15:04:44',20.5,'2021-07-26 15:04:32'),(246,'sciao','2021-07-26 15:04:46',20.5,'2021-07-26 15:04:32'),(247,'sciao','2021-07-26 15:09:00',20.5,'2021-07-26 15:08:48'),(248,'sciao','2021-07-26 15:09:02',20.5,'2021-07-26 15:08:48'),(249,'sciao','2021-07-26 15:27:27',20.5,'2021-07-26 15:27:15'),(250,'sciao','2021-07-26 15:27:27',20.5,'2021-07-26 15:27:15'),(251,'sciao','2021-07-26 15:36:54',20.5,'2021-07-26 15:36:42'),(252,'sciao','2021-07-26 15:36:54',20.5,'2021-07-26 15:36:42'),(253,'sciao','2021-07-26 15:36:54',20.5,'2021-07-26 15:36:42'),(254,'sciao','2021-07-26 15:42:12',20.5,'2021-07-26 15:42:00'),(255,'sciao','2021-07-26 15:42:12',20.5,'2021-07-26 15:42:00'),(256,'sciao','2021-07-26 15:42:12',20.5,'2021-07-26 15:42:00'),(257,'sciao','2021-07-26 16:26:22',20.5,'2021-07-26 16:26:10'),(258,'sciao','2021-07-26 16:26:22',20.5,'2021-07-26 16:26:10'),(259,'sciao','2021-07-26 16:26:22',20.5,'2021-07-26 16:26:10'),(260,'sciao','2021-07-26 16:29:00',20.5,'2021-07-26 16:28:48'),(261,'sciao','2021-07-26 16:29:00',20.5,'2021-07-26 16:28:47'),(262,'sciao','2021-07-26 16:29:00',20.5,'2021-07-26 16:28:47'),(263,'sciao','2021-07-26 16:32:27',20.5,'2021-07-26 16:30:35'),(264,'sciao','2021-07-26 16:32:27',20.5,'2021-07-26 16:30:35'),(265,'sciao','2021-07-26 16:43:08',20.5,'2021-07-26 16:41:50'),(266,'sciao','2021-07-26 16:43:10',20.5,'2021-07-26 16:41:50'),(267,'020002','2021-07-27 07:37:28',20.5,'2021-07-27 07:36:50'),(268,'020002','2021-07-27 07:37:28',20.5,'2021-07-27 07:36:50'),(269,'020002','2021-07-27 08:15:14',20.5,'2021-07-27 08:14:50'),(270,'020002','2021-07-27 08:15:14',20.5,'2021-07-27 08:14:50'),(271,'020002','2021-07-27 08:19:09',20.5,'2021-07-27 08:18:37'),(272,'020002','2021-07-27 08:19:09',20.5,'2021-07-27 08:18:37'),(273,'020002','2021-07-27 08:19:09',20.5,'2021-07-27 08:18:37'),(274,'020002','2021-07-27 08:20:56',20.5,'2021-07-27 08:20:26'),(275,'020002','2021-07-27 08:20:56',20.5,'2021-07-27 08:20:26'),(276,'020002','2021-07-27 08:20:56',20.5,'2021-07-27 08:20:26');
/*!40000 ALTER TABLE `price_display_state` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `weight_sensor_state`
--

DROP TABLE IF EXISTS `weight_sensor_state`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `weight_sensor_state` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `node_id` varchar(50) NOT NULL,
  `timestamp` timestamp NULL DEFAULT current_timestamp(),
  `current_weight` int(10) unsigned NOT NULL COMMENT 'unit=grams',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `weight_sensor_state`
--

LOCK TABLES `weight_sensor_state` WRITE;
/*!40000 ALTER TABLE `weight_sensor_state` DISABLE KEYS */;
/*!40000 ALTER TABLE `weight_sensor_state` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-07-27 10:29:53
