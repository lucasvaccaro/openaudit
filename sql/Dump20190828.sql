-- MySQL dump 10.13  Distrib 5.7.27, for Linux (x86_64)
--
-- Host: localhost    Database: openaudit
-- ------------------------------------------------------
-- Server version	5.7.27-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `report_isolation`
--

DROP TABLE IF EXISTS `report_isolation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `report_isolation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `snapshot_id` int(11) DEFAULT NULL,
  `host` varchar(255) DEFAULT NULL,
  `uuid` varchar(36) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_report_isolation_1_idx` (`snapshot_id`),
  CONSTRAINT `fk_report_isolation_1` FOREIGN KEY (`snapshot_id`) REFERENCES `snapshots` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `snapshot_isolation_compute`
--

DROP TABLE IF EXISTS `snapshot_isolation_compute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `snapshot_isolation_compute` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `snapshot_id` int(11) NOT NULL,
  `uuid` varchar(36) DEFAULT NULL,
  `host` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `snapshot_isolation_controller`
--

DROP TABLE IF EXISTS `snapshot_isolation_controller`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `snapshot_isolation_controller` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `snapshot_id` int(11) NOT NULL,
  `uuid` varchar(36) DEFAULT NULL,
  `host` varchar(255) DEFAULT NULL,
  `project_id` varchar(36) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_collector_openstackdb_isolation_1_idx` (`snapshot_id`),
  CONSTRAINT `fk_collector_openstackdb_isolation_1` FOREIGN KEY (`snapshot_id`) REFERENCES `snapshots` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `snapshot_routes_compute`
--

DROP TABLE IF EXISTS `snapshot_routes_compute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `snapshot_routes_compute` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `snapshot_id` int(11) DEFAULT NULL,
  `inet` varchar(32) DEFAULT NULL,
  `cidr` varchar(32) DEFAULT NULL,
  `gateway` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_snapshot_routes_compute_1_idx` (`snapshot_id`),
  CONSTRAINT `fk_snapshot_routes_compute_1` FOREIGN KEY (`snapshot_id`) REFERENCES `snapshots` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `snapshot_routes_controller`
--

DROP TABLE IF EXISTS `snapshot_routes_controller`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `snapshot_routes_controller` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `snapshot_id` int(11) DEFAULT NULL,
  `uuid` varchar(36) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `host` varchar(255) DEFAULT NULL,
  `cidr` varchar(32) DEFAULT NULL,
  `gateway_ip` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_snapshot_routes_controller_1_idx` (`snapshot_id`),
  CONSTRAINT `fk_snapshot_routes_controller_1` FOREIGN KEY (`snapshot_id`) REFERENCES `snapshots` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `snapshots`
--

DROP TABLE IF EXISTS `snapshots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `snapshots` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-08-28 20:34:19
