-- MySQL dump 10.13  Distrib 8.0.21, for Win64 (x86_64)
--
-- Host: localhost    Database: smartroster
-- ------------------------------------------------------
-- Server version	8.0.21

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `reference_page`
--

DROP TABLE IF EXISTS `reference_page`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reference_page` (
  `id` int NOT NULL AUTO_INCREMENT,
  `clinical_area` varchar(1500) DEFAULT NULL,
  `rotation` varchar(1500) DEFAULT NULL,
  `group_def` varchar(1000) DEFAULT NULL,
  `fte` varchar(1000) DEFAULT NULL,
  `skill_level` varchar(1500) DEFAULT NULL,
  `a_trained` varchar(1500) DEFAULT NULL,
  `transfer` varchar(1500) DEFAULT NULL,
  `iv_trained` varchar(1500) DEFAULT NULL,
  `advanced_role` varchar(1500) DEFAULT NULL,
  `dta` varchar(1500) DEFAULT NULL,
  `fixed_` varchar(1000) DEFAULT NULL,
  `flexible` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reference_page`
--

LOCK TABLES `reference_page` WRITE;
/*!40000 ALTER TABLE `reference_page` DISABLE KEYS */;
INSERT INTO `reference_page` VALUES (1,'Section which the nurse is assigned to (e.g. A,B,C,D,E, etc.)','Indicates when and which area a nurse rotates to from their usual clinical area (e.g. A01, B04, AB05, etc.)','Group in which the nurse is assigned (1, 2, 3 ,4, etc.)','Full Time Equivalent i.e. can be booked for full time (0 is NOT FTE, 1 is FTE)','A general scale to determine nurse skill level related to being acute trained, CPAP trained, ventilator trained, advanced acute trained (on a scale from 1 to 5)','Whether a nurse has specialty training (yes or no)','Whether a nurse is trained in patient transport (yes or no)','Whether a nurse is trained in administrating IV drips (yes or no)','Indicates the advanced roles a nurse is trained to perform. The L prior to the role name indicates a nurse is currently in training to a particular role (Charge, Support, Code)sd','Duty to Accommodate i.e. restrictions on the types of patient a nurse can be assigned tosd','Group of nurses that should be maintained in their patient assignment','Group of nurses to fill support roles, bumped if conflict with fixed nurse in patient assignment');
/*!40000 ALTER TABLE `reference_page` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-12-03 20:26:21
