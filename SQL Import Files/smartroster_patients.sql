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
-- Table structure for table `patients`
--

DROP TABLE IF EXISTS `patients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patients` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `clinical_area` varchar(100) DEFAULT NULL,
  `bed_num` int DEFAULT NULL,
  `acuity` int DEFAULT NULL,
  `a_trained` tinyint(1) DEFAULT NULL,
  `transfer` tinyint(1) DEFAULT NULL,
  `iv` tinyint(1) DEFAULT NULL,
  `one_to_one` tinyint(1) DEFAULT NULL,
  `previous_nurses` varchar(250) DEFAULT NULL,
  `admission_date` varchar(250) DEFAULT NULL,
  `discharged_date` varchar(250) DEFAULT NULL,
  `comments` varchar(250) DEFAULT NULL,
  `twin` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patients`
--

LOCK TABLES `patients` WRITE;
/*!40000 ALTER TABLE `patients` DISABLE KEYS */;
INSERT INTO `patients` VALUES (2,'Laurel Lawrence','F',3,5,1,0,0,0,'[2,5]','2020-11-18','','',0),(4,'Aliyah Whittle','F',5,5,1,1,1,1,'[29]','2020-11-19','2020-11-20','1',1),(5,'Tudor Krueger','F',6,3,1,0,1,1,'[]','2020-11-18','2020-11-20','',1),(6,'Ariella Hussain','F',9,5,1,0,0,1,'[5,6]','2020-11-18','-','',0),(7,'Lauren Bolton','E',1,2,0,0,0,0,'[]','2020-11-18','-','',1),(8,'Kia Bolton','E',1,2,1,0,0,0,'[]','2020-11-18','-','',1),(9,'Harley Reid','E',3,4,0,1,0,0,'[]','2020-11-18','-','',0),(10,'Kieran Hodgson','E',4,1,0,0,0,0,'[]','2020-11-18','-','',0),(11,'Olivia Fuller','E',5,4,0,0,0,0,'[]','2020-11-18','-','',0),(12,'Nile Russo','E',6,1,0,0,0,0,'[]','2020-11-18','-','',0),(13,'Frida Porter','E',7,1,0,0,0,0,'[]','2020-11-18','-','',0),(14,'Shayne Lane','E',8,2,0,0,0,0,'[]','2020-11-18','-','',0),(15,'Daisie Cohen','E',9,2,0,0,0,0,'[]','2020-11-18','-','',0),(16,'Aedan Sutherland','D',1,2,0,1,0,0,'[]','2020-11-18','-','',0),(17,'Kathryn Kendall','D',2,5,0,0,0,1,'[8]','2020-11-18','-','',0),(18,'Rosalie Callaghan','D',3,2,0,0,0,0,'[]','2020-11-18','-','',0),(19,'Kanye Wicks','D',4,3,0,0,0,0,'[]','2020-11-18','-','',0),(20,'Geoffrey Jimenez','D',5,4,0,0,0,0,'[]','2020-11-18','-','',0),(21,'Jordon Rhodes','D',6,1,0,0,0,0,'[11, 2]','2020-11-18','-','',0),(22,'Preston Krause','D',7,4,0,0,0,0,'[]','2020-11-18','-','',0),(23,'Brenda Livingston','D',8,2,0,0,0,0,'[]','2020-11-18','-','',0),(24,'Tate Thomson','D',9,2,0,0,0,0,'[]','2020-11-18','-','',0),(25,'Maxime Naylor','D',10,3,0,0,0,0,'[]','2020-11-18','-','',0),(26,'Bentley Schneider','E',10,4,0,0,0,0,'[]','2020-11-18','-','',0),(27,'Kaitlyn Lord','C',10,5,0,1,0,1,'[1,16]','2020-11-18','-','',0),(28,'Spencer Waller','D',11,4,0,0,0,0,'[]','2020-11-18','-','',0),(29,'Kady Franks','F',14,3,0,0,0,0,'[]','2020-11-18','-','',0),(30,'Bruce Baxter','C',12,5,0,0,0,0,'[]','2020-11-18','-','',1),(31,'Sofia Patel','E',11,2,0,0,0,0,'[]','2020-11-18','-','',0),(32,'Avi Salgado','F',4,3,0,1,0,0,'[]','2020-11-18','-','',0),(33,'Fenella Velazquez','C',5,4,0,0,0,0,'[]','2020-11-18','-','',0),(34,'Zaine Merritt','B',1,2,0,0,0,0,'[]','2020-11-18','-','',0),(35,'Cassie Lozano','F',4,3,0,0,0,0,'[]','2020-11-18','-','',0),(36,'Willie Mcnamara','C',6,3,0,0,0,0,'[]','2020-11-18','-','',0),(37,'Philippa Montes','A',7,4,0,0,0,0,'[]','2020-11-18','-','',0),(38,'Robin Hendricks','D',12,2,0,0,0,0,'[]','2020-11-18','-','',0),(39,'Kaci Porter','F',10,1,0,0,0,0,'[]','2020-11-18','-','',0),(40,'Kathleen Farrow','F',11,5,0,0,0,0,'[]','2020-11-18','-','',0),(41,'Merryn Fellows','E',12,1,0,0,0,0,'[]','2020-11-18','-','',0),(42,'Scarlet Odling','C',4,2,0,0,0,0,'[]','2020-11-18','-','',0),(43,'Dillan Pearson','C',2,3,0,0,0,0,'[]','2020-11-18','-','',0),(44,'Conrad Quintana','C',3,5,0,0,0,0,'[]','2020-11-18','-','',0),(45,'Rhea Christensen','F',6,3,0,1,0,0,'[]','2020-11-18','-','',0),(46,'Kate Montgomery','D',13,2,0,0,0,0,'[]','2020-11-18','-','',0),(47,'Sherry Searle','D',14,4,0,0,0,0,'[]','2020-11-18','-','',0),(48,'Emilis Burris','E',13,4,0,0,0,0,'[]','2020-11-18','-','',0),(49,'Douglas Webber','C',1,4,0,0,0,0,'[]','2020-11-18','-','',0),(50,'Jamaal Mackenzie','C',7,2,0,0,0,0,'[]','2020-11-18','-','',0),(51,'Jadine Hines','D',3,1,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(52,'Janine Morley','F',4,5,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(53,'Piper Mcdowell','E',1,3,0,1,0,0,'[]','2020-11-18','10/30/2020','',0),(54,'Rafael Alfaro','D',7,1,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(55,'Orion Macdonald','D',4,2,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(56,'Rui Stevens','F',3,2,1,0,0,0,'[]','2020-11-18','10/30/2020','',0),(57,'Fraser Klein','D',6,3,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(58,'Garrett Carlson','F',1,1,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(59,'Lacey Crowther','F',10,1,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(60,'Carolina Collier','F',5,4,1,0,0,0,'[]','2020-11-18','10/30/2020','',0),(61,'Carol Cortes','E',13,2,0,1,0,0,'[]','2020-11-18','10/30/2020','',0),(62,'Caroline Conrad','C',14,5,0,0,0,1,'[]','2020-11-18','10/30/2020','',0),(63,'Shay Mcmillan','A',2,2,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(64,'Joann Denton','F',6,3,1,0,0,0,'[]','2020-11-18','10/30/2020','',0),(65,'Octavia Perry','C',7,1,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(66,'Octavio Schneider','C',9,4,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(67,'Mitchel Cohen','E',4,4,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(68,'Edgar Laing','D',3,2,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(69,'Nikita Britt','F',6,3,1,0,0,0,'[]','2020-11-18','10/30/2020','',0),(70,'Jonathon Ritter','C',7,3,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(71,'Mabel Haynes','E',2,2,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(72,'Charli Hill','E',5,1,1,0,0,1,'[]','2020-11-18','10/30/2020','',0),(73,'Dixie Richards','E',6,1,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(74,'Trixie Roberson','E',9,1,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(75,'Joy Baxter','B',10,2,0,0,0,0,'[]','2020-11-18','10/30/2020','',1),(76,'Marianne Bernal','F',11,4,1,0,0,0,'[]','2020-11-18','10/30/2020','',0),(77,'Cecilia Hsieh','C',13,3,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(78,'Julianna Savage','F',6,2,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(79,'Ronaldo Saunders','F',4,1,0,1,0,0,'[]','2020-11-18','10/30/2020','',0),(80,'Ethan Brokowski','F',8,2,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(81,'Sofia Owen','E',2,1,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(82,'Justin Mcfarlane','C',3,3,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(83,'Eugene Cooley','B',8,2,0,1,0,0,'[]','2020-11-18','10/30/2020','',0),(84,'Michael Leal','F',4,4,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(85,'Meagan Odonnell','E',9,2,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(86,'Kyla Browne','D',10,1,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(87,'Kaye Nixon','F',14,4,1,1,0,0,'[]','2020-11-18','10/30/2020','',0),(88,'Matthew Douglas','D',2,3,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(89,'Johnny Chambers','F',6,2,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(90,'John Worthington','E',8,1,1,0,0,0,'[]','2020-11-18','10/30/2020','',0),(91,'Kevin Wilkins','D',3,3,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(92,'Daniel Sharma','E',5,5,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(93,'Keane Mcintosh','C',8,1,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(94,'Jacob Mohamed','E',2,2,1,0,0,0,'[]','2020-11-18','10/30/2020','',0),(95,'Marc Holmes','E',1,4,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(96,'Nathan Henderson','D',1,3,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(97,'Tommy Page','F',4,2,1,0,0,0,'[]','2020-11-18','10/30/2020','',0),(98,'Tyler Barnes','C',10,3,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(99,'Tyronne Hoover','D',1,2,0,0,0,0,'[]','2020-11-18','10/30/2020','',0),(100,'Bryan Saunders','C',12,1,0,0,0,0,'[]','2020-11-18','10/30/2020','',0);
/*!40000 ALTER TABLE `patients` ENABLE KEYS */;
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
