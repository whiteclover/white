SET @saved_cs_client = @@character_set_client;
SET character_set_client = utf8;


DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
	`uid` MEDIUMINT(8) unsigned NOT NULL AUTO_INCREMENT,
	`username` varchar(140) NOT NULL,
	`real_name` varchar(140) NOT NULL,
	`email` VARCHAR(140) NOT NULL,
	`password` CHAR(56) NOT NULL,
	`bio` text NOT NULL,
  `status` enum('inactive','active') NOT NULL,
  `role` enum( 'root', 'administrator','editor','user') NOT NULL,

	PRIMARY KEY (`uid`),
	UNIQUE KEY (`email`)

) ENGINE=InnoDB DEFAULT CHARSET=utf8;


LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'white','White','white@demo.com','a3748bcca4dca4afe824c3342bd0ba5a8da3f397f8c2822861c8e301','','active','root');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;


DROP TABLE IF EXISTS `pages`;
CREATE TABLE `pages` (
  `pid` int(6) NOT NULL AUTO_INCREMENT,
  `parent` int(6) NOT NULL,
  `slug` varchar(150) NOT NULL,
  `name` varchar(64) NOT NULL,
  `title` varchar(150) NOT NULL,
  `content` text NOT NULL,
  `status` enum('draft','published','archived') NOT NULL,
  `redirect` text NOT NULL,
  `show_in_menu` tinyint(1) NOT NULL,
  `menu_order` int(4) DEFAULT NULL,
  PRIMARY KEY (`pid`),
  KEY `status` (`status`),
  KEY `slug` (`slug`)
) ENGINE=InnoDB CHARSET=utf8;

LOCK TABLES `pages` WRITE;
/*!40000 ALTER TABLE `pages` DISABLE KEYS */;
INSERT INTO `pages` VALUES (1,0,'posts','Posts','My posts and thoughts','Welcome!','published','',1,NULL),(2,0,'about','About','About','This is A  about demo Page','published','',1,NULL),(3,0,'redirect','/redirect/demo','Redirect','This a redirect page','archived','',0,NULL);
/*!40000 ALTER TABLE `pages` ENABLE KEYS */;
UNLOCK TABLES;


DROP TABLE IF EXISTS `categories`;
CREATE TABLE `categories` (
  `cid` int(6) NOT NULL AUTO_INCREMENT,
  `title` varchar(150) NOT NULL,
  `slug` varchar(40) NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`cid`)
) ENGINE=InnoDB CHARSET=utf8;

INSERT INTO `categories` (`cid`, `title`, `slug`, `description`) VALUES (1, 'Uncategorised', 'uncategorised', 'Ain\'t no category here.');


DROP TABLE IF EXISTS `posts`;
CREATE TABLE `posts` (
  `pid` int(6) NOT NULL AUTO_INCREMENT,
  `title` varchar(150) NOT NULL,
  `slug` varchar(150) NOT NULL,
  `description` text NOT NULL,
  `html` text NOT NULL,
  `css` text NOT NULL,
  `js` text NOT NULL,
  `updated` datetime NOT NULL,
  `created` datetime NOT NULL,
  `author` int(6) NOT NULL,
  `category` int(6) NOT NULL,
  `status` enum('draft','published','archived') NOT NULL,
  `allow_comment` tinyint(1) NOT NULL,

  PRIMARY KEY (`pid`),
  KEY `status` (`status`),
  KEY `slug` (`slug`)
) ENGINE=InnoDB CHARSET=utf8;


LOCK TABLES `posts` WRITE;
/*!40000 ALTER TABLE `posts` DISABLE KEYS */;
INSERT INTO `posts` VALUES (1,'Hello White','hello-white','','Hello White!!!','','','2015-03-09 19:56:09','2015-03-09 19:55:05',1,1,'published',0),(2,'clover','clover','','**It was a buried memory.**\r\n\r\n**It was an eternal oath.**\r\n\r\n**It was a wish from the heart.**\r\n\r\n**It was a regret kept for eternity.**','','','2015-03-09 19:57:20','2015-03-09 19:55:45',1,1,'published',1);
/*!40000 ALTER TABLE `posts` ENABLE KEYS */;
UNLOCK TABLES;

DROP TABLE IF EXISTS `comments`;
CREATE TABLE `comments` (
  `cid` int(6) NOT NULL AUTO_INCREMENT,
  `post_id` int(6) NOT NULL,
  `status` enum('pending','approved','spam') NOT NULL,
  `name` varchar(140) NOT NULL,
  `email` varchar(140) NOT NULL,
  `content` text NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`cid`),
  KEY `post_id` (`post_id`),
  KEY `status` (`status`)
) ENGINE=InnoDB CHARSET=utf8;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES (1,2,'approved','White','white@demo.com','This a Test :)','2015-03-09 19:57:46');
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;

DROP TABLE IF EXISTS `extend`;
CREATE TABLE `extend` (
  `eid` int(6) NOT NULL AUTO_INCREMENT,
  `type` enum('post','page') NOT NULL,
  `field` enum('text','html','image','file') NOT NULL,
  `key` varchar(160) NOT NULL,
  `label` varchar(160) NOT NULL,
  `attributes` text NOT NULL,
  PRIMARY KEY (`eid`)
) ENGINE=InnoDB CHARSET=utf8;


DROP TABLE IF EXISTS `meta`;
CREATE TABLE `meta` (
  `mid` int(6) NOT NULL AUTO_INCREMENT,
  `node_id` int(6) NOT NULL,
  `type` enum('page', 'post') NOT NULL,
  `extend` int(6) NOT NULL,
  `data` text NOT NULL,
  PRIMARY KEY (`mid`),
  KEY `extend` (`extend`),
  UNIQUE KEY (`node_id`, `type`)
) ENGINE=InnoDB CHARSET=utf8;


DROP TABLE IF EXISTS `storage`;
CREATE TABLE `storage` (
  `key` varchar(140) NOT NULL,
  `value` text NOT NULL,
  PRIMARY KEY (`key`)
) ENGINE=InnoDB CHARSET=utf8;



LOCK TABLES `storage` WRITE;
/*!40000 ALTER TABLE `storage` DISABLE KEYS */;
INSERT INTO `storage` VALUES ('system','{\"auto_published_comments\": true, \"comment_moderation_keys\": [], \"comment_notifications\": false, \"description\": \"White is a Blog system\", \"posts_per_page\": 10, \"site_page\": 0, \"sitename\": \"White\"}');
/*!40000 ALTER TABLE `storage` ENABLE KEYS */;
UNLOCK TABLES;

SET @@character_set_client = @saved_cs_client;