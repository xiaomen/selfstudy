/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_admin_uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `building` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `campus_id` int(11) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `seq` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `campus_id` (`campus_id`),
  CONSTRAINT `building_ibfk_1` FOREIGN KEY (`campus_id`) REFERENCES `campus` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `buildings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `university_id` int(11) DEFAULT NULL,
  `campus_id` int(11) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `no` varchar(20) DEFAULT NULL,
  `enabled` tinyint(1) DEFAULT NULL,
  `seq` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `university_id` (`university_id`),
  KEY `campus_id` (`campus_id`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `campus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `university_id` int(11) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `seq` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `university_id` (`university_id`),
  CONSTRAINT `campus_ibfk_1` FOREIGN KEY (`university_id`) REFERENCES `university` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `campuses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `university_id` int(11) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `no` varchar(20) DEFAULT NULL,
  `seq` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `university_id` (`university_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `checkin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `building_id` int(11) NOT NULL,
  `classroom_id` int(11) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `message` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_checkin_uid` (`uid`),
  KEY `ix_checkin_classroom_id` (`classroom_id`),
  KEY `ix_checkin_building_id` (`building_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `classroom` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `building_id` int(11) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `capacity` int(11) DEFAULT NULL,
  `seq` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `building_id` (`building_id`),
  CONSTRAINT `classroom_ibfk_1` FOREIGN KEY (`building_id`) REFERENCES `building` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `classrooms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `building_id` int(11) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `no` varchar(20) DEFAULT NULL,
  `capacity` int(11) DEFAULT NULL,
  `seq` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `building_id` (`building_id`)
) ENGINE=InnoDB AUTO_INCREMENT=388 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `course` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `classroom_id` int(11) DEFAULT NULL,
  `start_week` int(11) DEFAULT NULL,
  `end_week` int(11) DEFAULT NULL,
  `day` int(11) DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `week_sign` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `classroom_id` (`classroom_id`),
  CONSTRAINT `course_ibfk_1` FOREIGN KEY (`classroom_id`) REFERENCES `classroom` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `feedback` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `classroom_id` int(11) NOT NULL,
  `occupy` tinyint(1) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_feedback_uid` (`uid`),
  KEY `ix_feedback_classroom_id` (`classroom_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `occupies` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `classroom_id` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `occupies` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `classroom_id` (`classroom_id`)
) ENGINE=InnoDB AUTO_INCREMENT=14239 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `period` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `university_id` int(11) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `start` int(11) DEFAULT NULL,
  `end` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `university_id` (`university_id`),
  CONSTRAINT `period_ibfk_1` FOREIGN KEY (`university_id`) REFERENCES `university` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `periods` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `university_id` int(11) DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `start` int(11) DEFAULT NULL,
  `end` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `university_id` (`university_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `universities` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `no` varchar(20) DEFAULT NULL,
  `class_quantity` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `university` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `no` varchar(20) DEFAULT NULL,
  `class_quantity` int(11) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
