-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: localhost    database: yuewei
-- ------------------------------------------------------
-- Server version	8.0.36

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `book`
--

DROP TABLE IF EXISTS `book`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `book` (
  `id` int NOT NULL AUTO_INCREMENT,
  `isbn` varchar(32) NOT NULL COMMENT 'ISBN',
  `title` varchar(128) NOT NULL COMMENT '标题',
  `origin_title` varchar(128) DEFAULT NULL COMMENT '原作名',
  `subtitle` varchar(128) DEFAULT NULL COMMENT '副标题',
  `author` varchar(128) NOT NULL COMMENT '作者',
  `page` int DEFAULT NULL COMMENT '页数',
  `publish_date` date DEFAULT NULL COMMENT '出版日期',
  `publisher` varchar(32) DEFAULT NULL COMMENT '出版社',
  `description` text COMMENT '简介',
  `douban_score` float DEFAULT NULL,
  `douban_id` varchar(24) DEFAULT NULL,
  `bangumi_score` float DEFAULT NULL,
  `bangumi_id` varchar(24) DEFAULT NULL,
  `type` enum('马列主义、毛泽东思想、邓小平理论','哲学、宗教','社会科学总论','政治、法律','军事','经济','文化、科学、教育、体育','语言、文字','文学','艺术','历史、地理','自然科学总论','数理科学和化学','天文学、地球科学','生物科学','医药、卫生','农业科学','工业技术','交通运输','航空、航天','环境科学、安全科学','综合性图书') DEFAULT NULL COMMENT '图书类型（参考自《中国图书馆图书分类法》）',
  PRIMARY KEY (`id`),
  UNIQUE KEY `isbn` (`isbn`),
  KEY `name` (`title`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `book`
--

LOCK TABLES `book` WRITE;
/*!40000 ALTER TABLE `book` DISABLE KEYS */;
INSERT INTO `book` VALUES (1,'9787508696010','老人与海','The Old Man and the Sea',NULL,'[美] 欧内斯特·海明威',264,'2018-11-01','中信出版社','“人可以被毁灭，但不能被打败。”一位老人孤身在海上捕鱼，八十四天一无所获，等终于钓到大鱼，用了两天两夜才将其刺死。返航途中突遭鲨鱼袭击，经过一天一夜的缠斗，大鱼仅存骨架。但老人并未失去希望和信心，休整之后，准备再次出海……\r\n编辑推荐\r\n◆ 海明威等了64年的中文译本终于来了！华语传奇作家鲁羊首次翻译外国经典，译稿出版前在各界名人中广泛流传，好评如潮，口碑爆棚。\r\n◆ 《老人与海》有声演读版音频，李蕾姐姐读经典演绎，用声音为你复活《老人与海》。\r\n◆ 附英文原版，校自海明威1952年亲自授权的美国Scribner原版定本！中英双语，超值典藏。\r\n◆ 国际当红女插画师SlavaShults，首次为中文版《老人与海》专门创作12副海报级手绘插图，带给你前所未有的阅读体验；随书附赠精1张精美明信片（一套10张随机送）。\r\n◆ “所有的原则自天而降：那就是你必须相信魔法，相信美，相信那些在百万个钻石中总结我们的人，相信此刻你手捧的鲁羊先生的译本，就是‘不朽’这个璀璨的词语给出的最好佐证。”——丁玲文学大奖、徐志摩诗歌金奖双奖得主何三坡\r\n◆“鲁羊的译文，其语言的简洁、节奏、语感、画面感和情感浓与淡的交错堪称完美，我感觉是海明威用中文写了《老人与海》，真棒！”——美籍华人知名学者、博士后导师邢若曦\r\n◆ 自1954年荣获诺贝尔文学奖至今，《老人与海》风靡全球，横扫每个必读经典书单，征服了亿万读者；据作家榜官方统计：截至2017年1月，113位诺贝尔文学奖得主作品中文版销量排行榜，海明威高居榜首，总销量突破550万册。\r\n◆ “人可以被毁灭，但不能被打败。”——本书作者海明威（诺贝尔文学奖、普利策奖双奖得主）',9,'30338134',8.3,'156705','文学'),(2,'9787535447340','文化苦旅',NULL,'余秋雨三十年散文自选集','余秋雨',287,'2014-04-01','长江文艺出版社','《文化苦旅》一书于1992年首次出版，是余秋雨先生1980年代在海内外讲学和考察途中写下的作品，是他的第一部文化散文集。全书主要包括两部分，一部分为历史、文化散文，另一部分为回忆散文。甫一面世，该书就以文采飞扬、知识丰厚、见解独到而备受万千读者喜爱。由此开创“历史大散文”一代文风，令世人重拾中华文化价值。他的散文别具一格，见常人所未见，思常人所未思，善于在美妙的文字中一步步将读者带入历史文化长河，启迪哲思，引发情致，具有极高的审美价值和史学、文化价值。书中多篇文章后入选中学教材。但由于此书的重大影响，在为余秋雨先生带来无数光环和拥趸的同时，也带来了数之不尽的麻烦和盗版。誉满天下，“谤”亦随身。余秋雨先生在身心俱疲之下，决定亲自修订、重编此书。\r\n新版《文化苦旅》作为余秋雨先生30年历史文化散文修订自选集，删掉旧版37篇文章中的13篇，新增文章17篇，其中入选教材的《道士塔》《莫高窟》《都江堰》等经典篇目全部经过改写、修订。新版内容与旧版相比，全新和改写的篇目达到三分之二以上，对新老读者都是一场全新的阅读体验和人文享受。堪称余秋雨30年来不懈的文化考察和人生思索的完美结晶。',8.2,'19940743',NULL,NULL,'文学'),(3,'9787801656087','明朝那些事儿（1-9）',NULL,'限量版','当年明月',NULL,'2009-04-01','中国海关出版社','《明朝那些事儿》讲述从1344年到1644年，明朝三百年间的历史。作品以史料为基础，以年代和具体人物为主线，运用小说的笔法，对明朝十七帝和其他王公权贵和小人物的命运进行全景展示，尤其对官场政治、战争、帝王心术着墨最多。作品也是一部明朝政治经济制度、人伦道德的演义。',9.2,'3674537',NULL,NULL,'历史、地理'),(4,'9787020084357','我与地坛',NULL,NULL,'史铁生',234,'2008-09-01','人民文学出版社','《我与地坛(纪念版)》是史铁生文学作品中，充满哲思又极为人性化的代表作之一。其前两段被纳入人民教育出版社的高一教材中。前两部分注重讲地坛和他与母亲的后悔，对中学生来说，这是一篇令人反思的优秀文章。',9.2,'6079389',NULL,NULL,'文学'),(5,'9787532776771','挪威的森林','ノルウェイの森',NULL,'[日] 村上春树',380,'2018-03-01','上海译文出版社','《挪威的森林》是日本作家村上春树所著的一部长篇爱情小说，影响了几代读者的青春名作。故事讲述主角渡边纠缠在情绪不稳定且患有精神疾病的直子和开朗活泼的小林绿子之间，苦闷彷徨，最终展开了自我救赎和成长的旅程。彻头彻尾的现实笔法，描绘了逝去的青春风景，小说中弥散着特有的感伤和孤独气氛。自1987年在日本问世后，该小说在年轻人中引起共鸣，风靡不息。上海译文出版社于2018年2月，推出该书的全新纪念版。',8.5,'27200257',8,'920','文学'),(6,'9787533936020','月亮与六便士','The Moon and Sixpence',NULL,'[英] 威廉·萨默塞特·毛姆',304,'2017-01-01','浙江文艺出版社','“满地都是六便士，他却抬头看见了月亮。”\r\n银行家查尔斯，人到中年，事业有成，为了追求内心隐秘的绘画梦想，突然抛妻别子，弃家出走。他深知：人的每一种身份都是一种自我绑架，唯有失去是通向自由之途。\r\n在异国他乡，他贫病交加，对梦想却愈发坚定执着。他说：我必须画画，就像溺水的人必须挣扎。\r\n在经历种种离奇遭遇后，他来到南太平洋的一座孤岛，同当地一位姑娘结婚生子，成功创作出一系列惊世杰作。就在此时，他被绝症和双目失明击倒，临死之前，他做出了让所有人震惊的决定……\r\n人世漫长得转瞬即逝，有人见尘埃，有人见星辰。查尔斯就是那个终其一生在追逐星辰的人。',8.7,'26954760',NULL,NULL,'文学');
/*!40000 ALTER TABLE `book` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat`
--

DROP TABLE IF EXISTS `chat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '这条信息的ID',
  `sender_id` int NOT NULL COMMENT '发信人ID',
  `receiver_id` int NOT NULL COMMENT '收信人ID',
  `content` text NOT NULL COMMENT '发信内容',
  `send_time` datetime NOT NULL COMMENT '发信时间',
  `is_read` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否查看',
  PRIMARY KEY (`id`),
  KEY `chat_user_id_fk` (`sender_id`),
  KEY `chat_user_id_fk2` (`receiver_id`),
  CONSTRAINT `chat_user_id_fk` FOREIGN KEY (`sender_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chat_user_id_fk2` FOREIGN KEY (`receiver_id`) REFERENCES `user` (`id`) ON DELETE SET DEFAULT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat`
--

LOCK TABLES `chat` WRITE;
/*!40000 ALTER TABLE `chat` DISABLE KEYS */;
/*!40000 ALTER TABLE `chat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `error`
--

DROP TABLE IF EXISTS `error`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `error` (
  `error_code` int NOT NULL,
  `title` varchar(128) NOT NULL,
  `title_en` varchar(128) NOT NULL,
  `content` text NOT NULL,
  `publish_time` datetime NOT NULL,
  `reference_link` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`error_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='该表用于存储定制的HTTP错误响应内容';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `error`
--

LOCK TABLES `error` WRITE;
/*!40000 ALTER TABLE `error` DISABLE KEYS */;
INSERT INTO `error` VALUES (400,'400错误：歪比歪比，歪比巴卜','[400]Bad Request.','这表示您的请求有些问题，服务器无法处理(戴夫：歪比巴卜？)。\n如果您在尝试自行访问本站的某个路由，请尝试修改请求方式或检查表单写法。\n如果是在正常访问时触发....好吧，看来后端又在写bug了，请与我们联系以帮忙改进。\n祝您生活愉快。','2024-04-03 15:49:09','https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status/400'),(403,'403错误：哒咩','[403]Forbidden.','这表示您查看的页面不允许您访问。\n通常来讲，这可能是由于您查看的页面要求登录，或需要管理员身份才能查看。\n如果您确信您的访问没有问题，那也许是某些奇怪的bug导致，请与我们联系。\n祝您生活愉快。','2024-04-03 17:34:24','https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status/403'),(404,'404错误：找不到您请求的资源','[404]Pages not Found.','如果您通过输入链接或收藏夹访问到该页面，这说明链接有误或有些文章已被删除或修改，不妨回到主页搜到那篇文章重新保存一下？ (oﾟvﾟ)ノ\n如果您在站内浏览时访问到该页面，这说明我们网站中某些跳转链接有误。இ௰இ您可以通过最下方的联系方式向我们反馈。感谢您对该项目的支持。\n如您还有其他意见/建议，同样欢迎与我们联系。\n祝您生活愉快。','2023-06-01 12:00:00','https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status/404'),(418,'418错误：我不能为你冲咖啡，因为我只是个茶壶','[418]I\'m a teapot.','这本身只是个玩笑，但现在这个响应多数时候表示服务器因爬虫而拒绝请求。也就是说，其实我已经看穿你用的是爬虫了。 ┏ (゜ω゜)=☞\n爬虫是个实用技术，但是下次记得稍微伪装一下，比如加个请求头啥的。 ε=ε=ε=(~￣▽￣)~\n并且注意要限制爬虫的速度，把别人服务器爬崩了可就摊上事了。 :\'(','2023-06-01 12:00:00','https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status/418'),(500,'500错误：服务器内部错误，暂时无法服务','[500]Internal Server Error.','这表示我们的服务器出现了内部错误இ௰இ，后端写的太烂又出问题了....\n后台小哥发现问题后会尽快定位修复，您也可以通过下方的联系方式向我们反馈。感谢您对该项目的支持。\n如您还有其他意见/建议，同样欢迎与我们联系。\n祝您生活愉快。','2023-06-01 12:00:00','https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status/500'),(503,'503错误：服务器当前不可用','[503]Service Unavailable.','这表示服务器目前不可用，可能是我们正在维护，或者租用的某个土豆服务器崩掉了。\n这应该不是我们的锅，但造成不好的使用体验，深感抱歉！','2023-06-08 15:08:06','https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status/503');
/*!40000 ALTER TABLE `error` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `group`
--

DROP TABLE IF EXISTS `group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL COMMENT '圈子的名称',
  `founder_id` int NOT NULL COMMENT '圈子创建者的ID',
  `establish_time` datetime NOT NULL,
  `description` text COMMENT '对该圈子的介绍',
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_name_uindex` (`name`),
  KEY `group_user_id_fk` (`founder_id`),
  CONSTRAINT `group_user_id_fk` FOREIGN KEY (`founder_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='圈子';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `group`
--

LOCK TABLES `group` WRITE;
/*!40000 ALTER TABLE `group` DISABLE KEYS */;
INSERT INTO `group` VALUES (1,'文学讨论小组',1,'2024-04-05 23:06:20','文以载道'),(2,'新闻观察小组',1,'2024-04-09 21:30:37','风声、雨声、读书声，声声入耳； 家事、国事、天下事，事事关心。');
/*!40000 ALTER TABLE `group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `group_discussion`
--

DROP TABLE IF EXISTS `group_discussion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `group_discussion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `poster_id` int NOT NULL,
  `group_id` int NOT NULL,
  `post_time` datetime NOT NULL COMMENT '创建时间',
  `title` varchar(256) NOT NULL COMMENT '帖子的标题',
  `content` text NOT NULL COMMENT '帖子内容',
  `is_read` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否查看',
  PRIMARY KEY (`id`),
  KEY `group_discussion_group_id_fk` (`group_id`),
  KEY `group_discussion_user_id_fk` (`poster_id`),
  CONSTRAINT `group_discussion_group_id_fk` FOREIGN KEY (`group_id`) REFERENCES `group` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `group_discussion_user_id_fk` FOREIGN KEY (`poster_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='讨论贴-圈子桥接表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `group_discussion`
--

LOCK TABLES `group_discussion` WRITE;
/*!40000 ALTER TABLE `group_discussion` DISABLE KEYS */;
INSERT INTO `group_discussion` VALUES (1,1,2,'2024-04-12 18:01:14','说来奇怪，为什么这么多青年人都喜欢熬夜呢','大家都知道熬夜对身体不好，为什么还有这么多人，一到晚上就躺在被窝里刷短视频，哈欠连天地看着别人的生活，也不好好睡觉，以更饱满的精神迎接明天呢？',1);
/*!40000 ALTER TABLE `group_discussion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `group_discussion_reply`
--

DROP TABLE IF EXISTS `group_discussion_reply`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `group_discussion_reply` (
  `author_id` int NOT NULL COMMENT '作者ID',
  `discussion_id` int NOT NULL COMMENT '讨论贴ID',
  `reply_time` datetime NOT NULL COMMENT '回复日期',
  `content` text NOT NULL COMMENT '回复内容',
  `is_read` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否查看',
  PRIMARY KEY (`author_id`,`discussion_id`,`reply_time`),
  KEY `discuss_reply_discuss_id_fk` (`discussion_id`),
  CONSTRAINT `group_discussion_reply_group_discussion_id_fk` FOREIGN KEY (`discussion_id`) REFERENCES `group_discussion` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `group_discussion_reply_user_id_fk` FOREIGN KEY (`author_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `group_discussion_reply`
--

LOCK TABLES `group_discussion_reply` WRITE;
/*!40000 ALTER TABLE `group_discussion_reply` DISABLE KEYS */;
INSERT INTO `group_discussion_reply` VALUES (1,1,'2024-04-15 02:22:26','熬夜，是现代人以灵魂抵押给深夜的无息贷款，用短暂的狂欢置换明日清醒的利息。',0),(1,1,'2024-04-16 15:19:45','我倒是觉得，熬夜可能只是表象而不是原因。有没有想过，现在年轻人的白天几乎是全部都给了工作，下班之后都9点了的大有人在，很多人没有时间去干点自己喜欢的事情，只有晚上躺在床上刷手机的时候才是“想看什么看什么”，才是真正属于自己的时间。',0),(1,1,'2024-04-16 15:20:34','扎心了老铁',0);
/*!40000 ALTER TABLE `group_discussion_reply` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `group_user`
--

DROP TABLE IF EXISTS `group_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `group_user` (
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  `join_time` datetime NOT NULL COMMENT '加入时间',
  PRIMARY KEY (`user_id`,`group_id`),
  KEY `group_user_group_id_fk` (`group_id`),
  CONSTRAINT `group_user_group_id_fk` FOREIGN KEY (`group_id`) REFERENCES `group` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `group_user_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户-圈子桥接表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `group_user`
--

LOCK TABLES `group_user` WRITE;
/*!40000 ALTER TABLE `group_user` DISABLE KEYS */;
INSERT INTO `group_user` VALUES (1,1,'2024-04-05 23:06:20'),(1,2,'2024-04-10 18:23:30');
/*!40000 ALTER TABLE `group_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `journal`
--

DROP TABLE IF EXISTS `journal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `journal` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `first_paragraph` text NOT NULL,
  `content` text NOT NULL,
  `publish_time` datetime NOT NULL,
  `author_id` int NOT NULL,
  `book_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `journal_user_id_fk` (`author_id`),
  KEY `journal_book_id_fk` (`book_id`),
  CONSTRAINT `journal_book_id_fk` FOREIGN KEY (`book_id`) REFERENCES `book` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `journal_user_id_fk` FOREIGN KEY (`author_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='书评';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `journal`
--

LOCK TABLES `journal` WRITE;
/*!40000 ALTER TABLE `journal` DISABLE KEYS */;
INSERT INTO `journal` VALUES (1,'人面不知何处去，桃花依旧笑春风','时光荏苒，岁月如梭。转眼间，又是一个春暖花开的季节。在这个美好的时光里，我独自漫步在桃林之中，心中不禁涌起一股莫名的感慨。','时光荏苒，岁月如梭。转眼间，又是一个春暖花开的季节。在这个美好的时光里，我独自漫步在桃林之中，心中不禁涌起一股莫名的感慨。\n桃林里，桃花盛开，一片繁花似锦。春风拂过，花瓣轻轻飘落，如梦如幻。此情此景，让我想起了那句脍炙人口的诗句：“人面不知何处去，桃花依旧笑春风。”\n这句诗，道出了人生的无常和自然的恒常。人世间的悲欢离合，犹如一场梦，而大自然却始终如一，桃花依旧笑春风。在这个瞬息万变的世界里，我们常常感叹人生的无常，无法预知未来。而大自然却始终坚守着它的规律，春暖花开，秋收冬藏，循环往复，永恒不变。\n漫步在桃林中，我看着那一张张熟悉的面孔，不禁想起了那些曾经陪伴我们走过的人和事。他们或许已经离去，或许已经不再联系我们，但他们的影子却永远留在了我们的心中。正如那句诗所说：“人面不知何处去”，他们的离去让我们感到惋惜和无奈，但我们也应该学会坦然面对，珍惜眼前的人和事。\n在这个春暖花开的季节里，让我们抛开烦恼和忧虑，尽情地欣赏大自然的美丽。让我们像桃花一样，笑对春风，笑对人生。无论人生如何变幻莫测，我们都要保持一颗乐观向上的心，珍惜眼前的每一刻，活出自己的精彩。\n人面不知何处去，桃花依旧笑春风。让我们怀揣着这句诗，漫步在人生的道路上，笑对风雨，笑对人生。','2024-04-02 14:22:14',1,2);
/*!40000 ALTER TABLE `journal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `journal_comment`
--

DROP TABLE IF EXISTS `journal_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `journal_comment` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  `publish_time` datetime NOT NULL COMMENT '发表日期',
  `author_id` int NOT NULL COMMENT '作者ID',
  `journal_id` int NOT NULL COMMENT '书评ID',
  `content` text NOT NULL COMMENT '评论内容',
  `is_read` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否查看',
  PRIMARY KEY (`id`),
  KEY `journal_comment_journal_id_fk` (`journal_id`),
  KEY `journal_comment_user_id_fk` (`author_id`),
  CONSTRAINT `journal_comment_journal_id_fk` FOREIGN KEY (`journal_id`) REFERENCES `journal` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `journal_comment_user_id_fk` FOREIGN KEY (`author_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `journal_comment`
--

LOCK TABLES `journal_comment` WRITE;
/*!40000 ALTER TABLE `journal_comment` DISABLE KEYS */;
INSERT INTO `journal_comment` VALUES (1,'2024-04-02 14:22:31',1,1,'文笔柔和，写的真不错！',1),(2,'2024-04-07 18:32:28',1,1,'但是好像写的有些不够深入，还需加油啊！',1);
/*!40000 ALTER TABLE `journal_comment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `journal_like`
--

DROP TABLE IF EXISTS `journal_like`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `journal_like` (
  `author_id` int NOT NULL COMMENT '作者ID',
  `journal_id` int NOT NULL COMMENT '书评ID',
  `publish_time` datetime NOT NULL COMMENT '发表日期',
  PRIMARY KEY (`author_id`,`journal_id`),
  KEY `journal_like_journal_id_fk` (`journal_id`),
  CONSTRAINT `journal_like_journal_id_fk` FOREIGN KEY (`journal_id`) REFERENCES `journal` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `journal_like_user_id_fk` FOREIGN KEY (`author_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='一个角色只能给某个书评点1个赞';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `journal_like`
--

LOCK TABLES `journal_like` WRITE;
/*!40000 ALTER TABLE `journal_like` DISABLE KEYS */;
INSERT INTO `journal_like` VALUES (1,1,'2024-04-04 13:54:22');
/*!40000 ALTER TABLE `journal_like` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `account` varchar(24) NOT NULL COMMENT '用户名',
  `password` text NOT NULL COMMENT '密码',
  `signature` varchar(128) DEFAULT '' COMMENT '签名档',
  `email` varchar(128) DEFAULT NULL COMMENT '邮箱',
  `telephone` varchar(11) DEFAULT NULL COMMENT '联系电话',
  `role` enum('student','teacher','admin') NOT NULL DEFAULT 'student' COMMENT '身份组',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_account_uindex` (`account`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'admin','scrypt:32768:8:1$ZVffw0BeuVvC3QfM$23a018d0a598367d12b371e9b655d7e338b2916def94f33bf81c2d6cd80888580ca188e467b78d968b886c6b59406bedeb3dbe0cb777d9bd428a7b4f6b75b6d5','道阻且长，行则将至！','Steven-Zhl@foxmail.com','15264051001','admin');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-04-17 19:35:56
