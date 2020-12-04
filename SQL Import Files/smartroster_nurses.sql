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
-- Table structure for table `nurses`
--

DROP TABLE IF EXISTS `nurses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `nurses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(250) DEFAULT '',
  `clinical_area` varchar(250) DEFAULT NULL,
  `bed_num` int DEFAULT NULL,
  `rotation` varchar(250) DEFAULT NULL,
  `group_num` int DEFAULT NULL,
  `fte` decimal(3,2) DEFAULT NULL,
  `skill_level` int DEFAULT NULL,
  `a_trained` tinyint(1) DEFAULT NULL,
  `transfer` tinyint(1) DEFAULT NULL,
  `iv` int DEFAULT NULL,
  `advanced_role` varchar(250) DEFAULT NULL,
  `previous_patients` varchar(250) DEFAULT NULL,
  `dta` varchar(250) DEFAULT '',
  `comments` varchar(250) DEFAULT '',
  `priority` int DEFAULT NULL,
  `current_shift` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nurses`
--

LOCK TABLES `nurses` WRITE;
/*!40000 ALTER TABLE `nurses` DISABLE KEYS */;
INSERT INTO `nurses` VALUES (1,'Rebecca Smith','B',1,'A01',1,0.50,5,0,0,3,'None','[27]','','',2,1),(2,'Holly Baker','D',3,'3',1,1.00,5,1,1,2,'Charge','[1, 2, 21]','1','1',2,1),(4,'Paige Lee','C',6,'AB02',1,1.00,4,1,0,1,'','[]','','Can\'t work next week',2,1),(5,'Hannah Moore','F',4,'A03',1,1.00,5,1,1,1,'L Code','[1, 2, 6]','','',2,1),(6,'Lily Marshall','D',7,'A02',1,1.00,5,1,0,1,'','[6]','Weight Limit: 25kg','',2,1),(7,'Emilia Carter','C',5,'AB05',1,1.00,2,0,0,1,'','[]','','',2,1),(8,'Maya Perry','C',2,'A06',1,1.00,5,1,0,1,'Support','[17]','','Can\'t work next week',2,1),(9,'Kelly Campbell','E',5,'B01',1,1.00,4,0,0,1,'','[]','Weight Limit: 25kg','',2,1),(10,'Kate Reyes','F',8,'B04',1,1.00,4,1,0,1,'','[]','','',2,1),(11,'Elise Diaz','E',6,'AB05',1,1.00,2,0,0,1,'','[21]','','',2,1),(12,'Erica Jackson','D',10,'B05',1,1.00,5,1,0,2,'Code','[]','Weight Limit: 25kg','Can\'t work next week',2,1),(13,'Freya Read','F',9,'A02',1,1.00,4,1,0,1,'','[]','','',2,1),(14,'Anne Jeffery','E',14,'A03',1,1.00,4,1,0,1,'','[]','','',2,1),(15,'Ayla Terry','E',1,'B03',1,1.00,5,1,1,2,'Charge','[]','Weight Limit: 25kg','',2,1),(16,'Ralph Erickson','C',4,'A05',1,1.00,5,1,1,2,'Charge','[27]','','Can\'t work next week',2,1),(17,'Frederick Graves','C',3,'A05',1,1.00,4,0,0,1,'','[]','','',2,1),(18,'Fraser Rogers','E',6,'B02',1,1.00,5,1,0,1,'Support','[]','Weight Limit: 25kg','',2,1),(19,'Troy Shaw','C',7,'A04',1,1.00,4,0,1,1,'','[]','','',2,1),(20,'Frederick Stewart','E',10,'B04',1,1.00,5,0,0,2,'Support','[]','','Can\'t work next week',2,1),(21,'Wayne Alexander','C',11,'B04',2,1.00,4,1,0,1,'','[]','Weight Limit: 25kg','',1,1),(22,'Herman Lopez','D',1,'B03',2,1.00,5,1,1,1,'','[]','','',1,1),(23,'Douglas Ryan','F',3,'M01',2,1.00,3,1,0,1,'','[24]','','',1,1),(24,'Liberty Bowers','E',6,'B01',2,1.00,5,1,0,2,'Charge','[]','Weight Limit: 25kg','Can\'t work next week',1,1),(25,'Tony Bowen','D',2,'A02',2,1.00,4,1,0,1,'','[]','','',1,1),(26,'Mason Martin','D',8,'AB05',2,1.00,3,0,0,1,'','[]','','',1,1),(27,'Hector Morris ','E',7,'B4+5',2,1.00,4,1,0,1,'','[]','Weight Limit: 25kg','',1,1),(28,'Robert Hopkins','E',5,'B02',2,1.00,5,1,0,1,'Code','[]','','Can\'t work next week',1,1),(29,'Adam Bauer','F',10,'A05',2,1.00,5,1,0,2,'Charge','[4]','','',1,1),(30,'Zack Arnold','F',12,'B03',2,1.00,5,1,0,2,'Charge','[]','Weight Limit: 25kg','',1,1),(31,'Kira Bishop','E',13,'A04',2,1.00,4,0,0,1,'','[]','','',1,1),(32,'Kane Matthews','D',2,'B04',2,1.00,5,0,1,1,'','[]','','Can\'t work next week',1,1),(33,'Faith Harrison','E',5,'B1+2',2,1.00,5,1,0,1,'Support','[]','Weight Limit: 25kg','',1,1),(34,'Jacob Griffin','C',3,'B06',2,1.00,4,1,0,1,'','[]','','',1,1),(35,'Alfie Paul','D',1,'A03',2,1.00,5,1,1,1,'Support','[]','','',1,1),(36,'Seth Lewis','D',6,'AB05',2,1.00,4,0,0,1,'L Support','[]','Weight Limit: 25kg','Can\'t work next week',1,1),(37,'Shawn Harmon','F',7,'AB06',2,1.00,1,0,0,1,'L Charge','[]','','',1,1),(38,'Daniel Robinson','C',1,'B05',2,1.00,5,1,0,1,'Support','[]','','',1,1),(39,'Gerald Harrison','D',9,'A04',2,1.00,4,1,0,1,'Code','[]','Weight Limit: 25kg','',1,1),(40,'Jack Benson','C',11,'B03',2,1.00,4,0,1,1,'','[]','','Can\'t work next week',1,1),(41,'Ben Oliver','D',13,'B04',3,1.00,5,1,0,1,'Charge','[]','','',0,0),(42,'Sommer Haynes','C',2,'B03',3,1.00,5,1,0,1,'Charge','[]','Weight Limit: 25kg','',0,0),(43,'Adam Griffith','C',5,'B06',3,1.00,5,1,0,2,'','[]','','',0,0),(44,'Kathryn Myers','D',4,'A05',3,1.00,4,1,0,1,'','[]','','Can\'t work next week',0,0),(45,'Ela Hamilton','E',3,'A06',3,1.00,4,1,0,1,'','[]','Weight Limit: 25kg','',0,0),(46,'Luke Whelan','E',8,'B02',3,1.00,5,1,0,1,'','[]','','',0,0),(47,'Lloyd Luna','C',5,'B06',3,1.00,5,1,0,1,'Support','[]','','',0,0),(48,'Jaguar Colon','A',6,'A01',3,1.00,5,1,1,2,'','[]','Weight Limit: 25kg','Can\'t work next week',0,0),(49,'Jimmy Webster','F',11,'B03',3,1.00,5,1,0,1,'','[]','','',0,0),(50,'Eugene Glover','D',14,'A01',3,1.00,4,0,0,1,'','[]','','',0,0),(51,'Miguel Rose','E',10,'A02',3,1.00,2,1,0,1,'','[]','Weight Limit: 25kg','',0,0),(52,'Nicholas Thorne','C',5,'A05',3,1.00,4,0,0,1,'','[]','','Can\'t work next week',0,0),(53,'Zach Atherton','D',6,'B04',3,1.00,5,1,0,2,'','[]','','',0,0),(54,'Nathan Greeme','F',3,'B02',3,1.00,5,1,0,1,'','[]','Weight Limit: 25kg','',0,0),(55,'Cheryl Castillo','C',7,'B04',3,1.00,4,1,0,1,'','[]','','',0,0),(56,'Dana Hicks','E',1,'B01',3,1.00,4,0,0,1,'','[]','','Can\'t work next week',0,0),(57,'Scott Ramsey','F',8,'B06',3,1.00,5,0,1,1,'','[]','Weight Limit: 25kg','',0,0),(58,'Benjamin Bradley','C',7,'A04',3,1.00,5,1,0,1,'','[]','','',0,0),(59,'Carmen Brtiggs','C',9,'B01',3,1.00,5,1,0,2,'','[]','','',0,0),(60,'Georgie Powell','C',6,'A06',3,1.00,5,0,0,1,'L Support','[]','Weight Limit: 25kg','Can\'t work next week',0,0),(61,'Crystal Keller','C',5,'A06',4,1.00,5,1,0,1,'Support','[]','','',0,0),(62,'Eva Wang','A',8,'M06',4,1.00,2,0,0,1,'','[]','','',0,0),(63,'Edith Rodriguez','D',1,'AB04',4,1.00,3,0,0,1,'','[]','Weight Limit: 25kg','',0,0),(64,'Josie Johnston','F',3,'B06',4,1.00,5,1,0,1,'Support','[]','','Can\'t work next week',0,0),(65,'Kimberly Smith','A',2,'M02',4,1.00,2,1,0,1,'','[]','','',0,0),(66,'Samantha Wise','E',2,'A03',4,1.00,3,1,0,1,'','[]','Weight Limit: 25kg','',0,0),(67,'Taylor Baker','C',9,'A03',4,1.00,5,1,0,1,'Support','[]','','',0,0),(68,'Tiffany Mcgregor','C',6,'A01',4,1.00,5,1,0,1,'Support','[]','','Can\'t work next week',0,0),(69,'Flora Gonzalez','C',10,'B05',4,1.00,5,1,1,1,'Support','[]','Weight Limit: 25kg','',0,0),(70,'Mia Davis','F',13,'B06',4,1.00,5,1,0,1,'','[]','','',0,0),(71,'Leona Wilson','D',5,'B03',4,1.00,4,0,0,1,'','[]','','',0,0),(72,'Hayley Payne','D',3,'B03',4,1.00,5,0,0,1,'','[]','Weight Limit: 25kg','Can\'t work next week',0,0),(73,'Ashlee  Pena','E',7,'A04',4,1.00,5,1,1,2,'Charge','[]','','',0,0),(74,'Digby  Mckinney','D',1,'B05',4,1.00,5,0,0,1,'Support','[]','','',0,0),(75,'Tiana  Ross','D',4,'B04',4,1.00,5,1,0,1,'Code','[]','Weight Limit: 25kg','',0,0),(76,'Megan Montoya','D',11,'B06',4,1.00,5,1,0,1,'Charge','[]','','Can\'t work next week',0,0),(77,'Jerry Mendoza','F',6,'AB02',4,1.00,3,0,0,1,'','[]','','',0,0),(78,'Bailey Robertson','E',5,'B01',4,1.00,5,1,0,1,'Support','[]','Weight Limit: 25kg','',0,0),(79,'Alfie Patterson','D',7,'B05',4,1.00,5,0,0,1,'','[]','','',0,0),(80,'Kelly Conner',NULL,NULL,NULL,0,0.00,5,1,0,1,'','[]','','Can\'t work next week',0,0),(81,'Katy Schmidtt',NULL,NULL,NULL,0,0.00,5,1,0,1,'','[]','Weight Limit: 25kg','',0,0),(82,'Deborah Boyd',NULL,NULL,NULL,0,0.00,5,0,1,1,'L Code','[]','','',0,0),(83,'Beatrix Duncan',NULL,NULL,NULL,0,0.00,3,0,0,1,'','[]','','',0,0),(84,'Frederic Black',NULL,NULL,NULL,0,0.00,5,1,0,1,'','[]','Weight Limit: 25kg','Can\'t work next week',0,0),(85,'Edgar Clayton',NULL,NULL,NULL,0,0.00,3,0,0,1,'','[]','','',0,0),(86,'Melanie Riley',NULL,NULL,NULL,0,0.00,5,1,0,1,'','[]','','',0,0),(87,'Mike Starkey',NULL,NULL,NULL,0,0.00,5,0,0,1,'Code','[]','Weight Limit: 25kg','',0,0),(88,'Nancy Chapman',NULL,NULL,NULL,0,0.00,1,1,0,1,'','[]','','Can\'t work next week',0,0),(89,'Bruce Kennedy',NULL,NULL,NULL,0,0.00,3,0,0,1,'','[]','','',0,0),(90,'Brian Burton',NULL,NULL,NULL,0,0.00,4,1,1,1,'','[]','Weight Limit: 25kg','',0,0),(91,'Shane Henry',NULL,NULL,NULL,0,0.00,5,1,0,1,'L Charge','[]','','',0,0),(92,'Gary Bernard',NULL,NULL,NULL,0,0.00,4,0,0,1,'','[]','','Can\'t work next week',0,0),(93,'Katherine Faulkner',NULL,NULL,NULL,0,0.00,3,0,0,1,'','[]','Weight Limit: 25kg','',0,0),(94,'Wilbur Owens',NULL,NULL,NULL,0,0.00,3,0,0,1,'','[]','','',0,0),(95,'Raymond Welch',NULL,NULL,NULL,0,0.00,5,1,1,1,'Charge','[]','','',0,0),(96,'Russel Delgado',NULL,NULL,NULL,0,0.00,4,1,0,1,'','[]','Weight Limit: 25kg','Can\'t work next week',0,0),(97,'Jackson Mitchell',NULL,NULL,NULL,0,0.00,4,1,0,1,'','[]','','',0,0),(98,'Keith Dunn',NULL,NULL,NULL,0,0.00,4,0,0,1,'','[]','','',0,0),(99,'Taylor Alvarez',NULL,NULL,NULL,0,0.00,4,0,0,1,'','[]','Weight Limit: 25kg','',0,0),(100,'Rian Hartness',NULL,NULL,NULL,0,0.00,5,0,0,1,'','[]','','Can\'t work next week',0,0),(120,'Teresa Bagshawe','D',NULL,'A6',6,1.00,5,0,0,1,'Code',NULL,'','',0,0);
/*!40000 ALTER TABLE `nurses` ENABLE KEYS */;
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
