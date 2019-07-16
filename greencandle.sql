-- MySQL dump 10.16  Distrib 10.1.31-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: greencandle
-- ------------------------------------------------------
-- Server version	10.1.31-MariaDB

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
-- Table structure for table `action_totals`
--
CREATE DATABASE greencandle;
USE greencandle;

DROP TABLE IF EXISTS `action_totals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `action_totals` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `ctime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `pair` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `total` int(3) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `actions`
--

DROP TABLE IF EXISTS `actions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `actions` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `ctime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `pair` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `indicator` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `action` int(3) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `balance`
--

DROP TABLE IF EXISTS `balance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `balance` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `ctime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `exchange_id` int(11) unsigned NOT NULL,
  `gbp` varchar(30) DEFAULT NULL,
  `btc` varchar(30) DEFAULT NULL,
  `usd` varchar(30) DEFAULT NULL,
  `count` varchar(30) DEFAULT NULL,
  `coin` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `exchange_id` (`exchange_id`),
  CONSTRAINT `balance_ibfk_2` FOREIGN KEY (`exchange_id`) REFERENCES `exchange` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=90447 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `changes`
--

DROP TABLE IF EXISTS `changes`;
/*!50001 DROP VIEW IF EXISTS `changes`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `changes` (
  `ctime` tinyint NOT NULL,
  `pair` tinyint NOT NULL,
  `gt` tinyint NOT NULL,
  `lt` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `coin`
--

DROP TABLE IF EXISTS `coin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coin` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `symbol` varchar(10) DEFAULT NULL,
  `name` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `daily_growth_15m`
--

DROP TABLE IF EXISTS `daily_growth_15m`;
/*!50001 DROP VIEW IF EXISTS `daily_growth_15m`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `daily_growth_15m` (
  `cdate` tinyint NOT NULL,
  `Growth` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `daily_growth_1m`
--

DROP TABLE IF EXISTS `daily_growth_1m`;
/*!50001 DROP VIEW IF EXISTS `daily_growth_1m`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `daily_growth_1m` (
  `cdate` tinyint NOT NULL,
  `Growth` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `daily_growth_3m`
--

DROP TABLE IF EXISTS `daily_growth_3m`;
/*!50001 DROP VIEW IF EXISTS `daily_growth_3m`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `daily_growth_3m` (
  `cdate` tinyint NOT NULL,
  `Growth` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `daily_growth_5m`
--

DROP TABLE IF EXISTS `daily_growth_5m`;
/*!50001 DROP VIEW IF EXISTS `daily_growth_5m`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `daily_growth_5m` (
  `cdate` tinyint NOT NULL,
  `Growth` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `data`
--

DROP TABLE IF EXISTS `data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `symbol` varchar(10) DEFAULT NULL,
  `ctime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `event` varchar(20) DEFAULT NULL,
  `direction` varchar(20) DEFAULT NULL,
  `data` varchar(1000) DEFAULT NULL,
  `difference` varchar(5) DEFAULT NULL,
  `resistance` varchar(1000) DEFAULT NULL,
  `support` varchar(1000) DEFAULT NULL,
  `buy` varchar(20) DEFAULT NULL,
  `sell` varchar(20) DEFAULT NULL,
  `market` varchar(20) DEFAULT NULL,
  `balance` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exchange`
--

DROP TABLE IF EXISTS `exchange`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `exchange` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `growth_15m`
--

DROP TABLE IF EXISTS `growth_15m`;
/*!50001 DROP VIEW IF EXISTS `growth_15m`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `growth_15m` (
  `buy_time` tinyint NOT NULL,
  `sell_time` tinyint NOT NULL,
  `pair` tinyint NOT NULL,
  `buy_price` tinyint NOT NULL,
  `sell_price` tinyint NOT NULL,
  `Growth` tinyint NOT NULL,
  `total` tinyint NOT NULL,
  `total_btc` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `growth_1m`
--

DROP TABLE IF EXISTS `growth_1m`;
/*!50001 DROP VIEW IF EXISTS `growth_1m`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `growth_1m` (
  `buy_time` tinyint NOT NULL,
  `sell_time` tinyint NOT NULL,
  `pair` tinyint NOT NULL,
  `buy_price` tinyint NOT NULL,
  `sell_price` tinyint NOT NULL,
  `Growth` tinyint NOT NULL,
  `total` tinyint NOT NULL,
  `total_btc` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `growth_3m`
--

DROP TABLE IF EXISTS `growth_3m`;
/*!50001 DROP VIEW IF EXISTS `growth_3m`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `growth_3m` (
  `buy_time` tinyint NOT NULL,
  `sell_time` tinyint NOT NULL,
  `pair` tinyint NOT NULL,
  `buy_price` tinyint NOT NULL,
  `sell_price` tinyint NOT NULL,
  `Growth` tinyint NOT NULL,
  `total` tinyint NOT NULL,
  `total_btc` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `growth_5m`
--

DROP TABLE IF EXISTS `growth_5m`;
/*!50001 DROP VIEW IF EXISTS `growth_5m`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `growth_5m` (
  `buy_time` tinyint NOT NULL,
  `sell_time` tinyint NOT NULL,
  `pair` tinyint NOT NULL,
  `buy_price` tinyint NOT NULL,
  `sell_price` tinyint NOT NULL,
  `Growth` tinyint NOT NULL,
  `total` tinyint NOT NULL,
  `total_btc` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `historical`
--

DROP TABLE IF EXISTS `historical`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `historical` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `pair` varchar(7) DEFAULT NULL,
  `buckettime` datetime DEFAULT NULL,
  `low` float DEFAULT NULL,
  `high` float DEFAULT NULL,
  `open` float DEFAULT NULL,
  `close` float DEFAULT NULL,
  `volume` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `pair_2` (`pair`,`buckettime`),
  KEY `pair` (`pair`),
  KEY `buckettime` (`buckettime`),
  KEY `volume` (`volume`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `hour_balance`
--

DROP TABLE IF EXISTS `hour_balance`;
/*!50001 DROP VIEW IF EXISTS `hour_balance`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `hour_balance` (
  `exchange_id` tinyint NOT NULL,
  `usd1` tinyint NOT NULL,
  `coin` tinyint NOT NULL,
  `ctime1` tinyint NOT NULL,
  `ctime2` tinyint NOT NULL,
  `usd2` tinyint NOT NULL,
  `USD_diff` tinyint NOT NULL,
  `GBP_diff` tinyint NOT NULL,
  `COUNT_diff` tinyint NOT NULL,
  `perc_change` tinyint NOT NULL,
  `BTC_diff` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `profit_15m`
--

DROP TABLE IF EXISTS `profit_15m`;
/*!50001 DROP VIEW IF EXISTS `profit_15m`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `profit_15m` (
  `buy_time` tinyint NOT NULL,
  `sell_time` tinyint NOT NULL,
  `pair` tinyint NOT NULL,
  `Growth` tinyint NOT NULL,
  `total` tinyint NOT NULL,
  `total_btc` tinyint NOT NULL,
  `gbp_buy` tinyint NOT NULL,
  `gbp_sell` tinyint NOT NULL,
  `gbp_profit` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `profit_1m`
--

DROP TABLE IF EXISTS `profit_1m`;
/*!50001 DROP VIEW IF EXISTS `profit_1m`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `profit_1m` (
  `buy_time` tinyint NOT NULL,
  `sell_time` tinyint NOT NULL,
  `pair` tinyint NOT NULL,
  `Growth` tinyint NOT NULL,
  `total` tinyint NOT NULL,
  `total_btc` tinyint NOT NULL,
  `gbp_buy` tinyint NOT NULL,
  `gbp_sell` tinyint NOT NULL,
  `gbp_profit` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `profit_3m`
--

DROP TABLE IF EXISTS `profit_3m`;
/*!50001 DROP VIEW IF EXISTS `profit_3m`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `profit_3m` (
  `buy_time` tinyint NOT NULL,
  `sell_time` tinyint NOT NULL,
  `pair` tinyint NOT NULL,
  `Growth` tinyint NOT NULL,
  `total` tinyint NOT NULL,
  `total_btc` tinyint NOT NULL,
  `gbp_buy` tinyint NOT NULL,
  `gbp_sell` tinyint NOT NULL,
  `gbp_profit` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `profit_5m`
--

DROP TABLE IF EXISTS `profit_5m`;
/*!50001 DROP VIEW IF EXISTS `profit_5m`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `profit_5m` (
  `buy_time` tinyint NOT NULL,
  `sell_time` tinyint NOT NULL,
  `pair` tinyint NOT NULL,
  `Growth` tinyint NOT NULL,
  `total` tinyint NOT NULL,
  `total_btc` tinyint NOT NULL,
  `gbp_buy` tinyint NOT NULL,
  `gbp_sell` tinyint NOT NULL,
  `gbp_profit` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view `recent_actions`
--

DROP TABLE IF EXISTS `recent_actions`;
/*!50001 DROP VIEW IF EXISTS `recent_actions`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `recent_actions` (
  `id` tinyint NOT NULL,
  `ctime` tinyint NOT NULL,
  `pair` tinyint NOT NULL,
  `indicator` tinyint NOT NULL,
  `value` tinyint NOT NULL,
  `action` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `symbols`
--

DROP TABLE IF EXISTS `symbols`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `symbols` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `symbol` varchar(10) DEFAULT NULL,
  `category` varchar(20) DEFAULT NULL,
  `maximum_leverage` int(11) DEFAULT NULL,
  `maximum_amount` int(11) DEFAULT NULL,
  `overnight_charge_long_percent` float DEFAULT NULL,
  `overnight_charge_short_percent` float DEFAULT NULL,
  `decimals` int(11) DEFAULT NULL,
  `timezone` varchar(80) DEFAULT NULL,
  `timezone_offset` varchar(10) DEFAULT NULL,
  `open_day` varchar(80) DEFAULT NULL,
  `open_time` time DEFAULT NULL,
  `close_day` varchar(80) DEFAULT NULL,
  `close_time` time DEFAULT NULL,
  `daily_break_start` time DEFAULT NULL,
  `daily_break_stop` time DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `symbol` (`symbol`),
  KEY `category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `trades`
--

DROP TABLE IF EXISTS `trades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trades` (
  `buy_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `sell_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `pair` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `buy_price` decimal(10,10) DEFAULT NULL,
  `sell_price` decimal(10,10) DEFAULT NULL,
  `investment` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `trades_15m`
--

DROP TABLE IF EXISTS `trades_15m`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trades_15m` (
  `buy_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `sell_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `pair` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `buy_price` decimal(10,10) DEFAULT NULL,
  `sell_price` decimal(10,10) DEFAULT NULL,
  `investment` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `trades_1m`
--

DROP TABLE IF EXISTS `trades_1m`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trades_1m` (
  `buy_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `sell_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `pair` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `buy_price` decimal(10,10) DEFAULT NULL,
  `sell_price` decimal(10,10) DEFAULT NULL,
  `investment` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `trades_3m`
--

DROP TABLE IF EXISTS `trades_3m`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trades_3m` (
  `buy_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `sell_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `pair` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `buy_price` decimal(10,10) DEFAULT NULL,
  `sell_price` decimal(10,10) DEFAULT NULL,
  `investment` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `trades_5m`
--

DROP TABLE IF EXISTS `trades_5m`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trades_5m` (
  `buy_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `sell_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `pair` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `buy_price` decimal(10,10) DEFAULT NULL,
  `sell_price` decimal(10,10) DEFAULT NULL,
  `investment` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `trades_back`
--

DROP TABLE IF EXISTS `trades_back`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trades_back` (
  `buy_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `sell_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `pair` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `buy_price` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sell_price` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `investment` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `changes`
--

/*!50001 DROP TABLE IF EXISTS `changes`*/;
/*!50001 DROP VIEW IF EXISTS `changes`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`greencandle`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `changes` AS select `s1`.`ctime` AS `ctime`,`s1`.`pair` AS `pair`,((`s1`.`total` <= 0) and (`s2`.`total` >= 0)) AS `gt`,((`s1`.`total` >= 0) and (`s2`.`total` <= 0)) AS `lt` from (`action_totals` `s1` left join `action_totals` `s2` on((`s1`.`pair` = `s2`.`pair`))) where ((`s1`.`total` <> `s2`.`total`) and ((`s1`.`total` < 0) or (`s2`.`total` < 0)) and ((`s1`.`total` > 0) or (`s2`.`total` > 0))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `daily_growth_15m`
--

/*!50001 DROP TABLE IF EXISTS `daily_growth_15m`*/;
/*!50001 DROP VIEW IF EXISTS `daily_growth_15m`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`greencandle`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `daily_growth_15m` AS select left(`trades_15m`.`sell_time`,10) AS `cdate`,avg((((`trades_15m`.`sell_price` - `trades_15m`.`buy_price`) / `trades_15m`.`sell_price`) * 100)) AS `Growth` from `trades_15m` where (`trades_15m`.`sell_price` is not null) group by left(`trades_15m`.`sell_time`,10) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `daily_growth_1m`
--

/*!50001 DROP TABLE IF EXISTS `daily_growth_1m`*/;
/*!50001 DROP VIEW IF EXISTS `daily_growth_1m`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`greencandle`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `daily_growth_1m` AS select left(`trades_1m`.`sell_time`,10) AS `cdate`,avg((((`trades_1m`.`sell_price` - `trades_1m`.`buy_price`) / `trades_1m`.`sell_price`) * 100)) AS `Growth` from `trades_1m` where (`trades_1m`.`sell_price` is not null) group by left(`trades_1m`.`sell_time`,10) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `daily_growth_3m`
--

/*!50001 DROP TABLE IF EXISTS `daily_growth_3m`*/;
/*!50001 DROP VIEW IF EXISTS `daily_growth_3m`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`greencandle`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `daily_growth_3m` AS select left(`trades_3m`.`sell_time`,10) AS `cdate`,avg((((`trades_3m`.`sell_price` - `trades_3m`.`buy_price`) / `trades_3m`.`sell_price`) * 100)) AS `Growth` from `trades_3m` where (`trades_3m`.`sell_price` is not null) group by left(`trades_3m`.`sell_time`,10) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `daily_growth_5m`
--

/*!50001 DROP TABLE IF EXISTS `daily_growth_5m`*/;
/*!50001 DROP VIEW IF EXISTS `daily_growth_5m`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`greencandle`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `daily_growth_5m` AS select left(`trades_5m`.`sell_time`,10) AS `cdate`,avg((((`trades_5m`.`sell_price` - `trades_5m`.`buy_price`) / `trades_5m`.`sell_price`) * 100)) AS `Growth` from `trades_5m` where (`trades_5m`.`sell_price` is not null) group by left(`trades_5m`.`sell_time`,10) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `growth_15m`
--

/*!50001 DROP TABLE IF EXISTS `growth_15m`*/;
/*!50001 DROP VIEW IF EXISTS `growth_15m`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`greencandle`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `growth_15m` AS select `trades_15m`.`buy_time` AS `buy_time`,`trades_15m`.`sell_time` AS `sell_time`,`trades_15m`.`pair` AS `pair`,`trades_15m`.`buy_price` AS `buy_price`,`trades_15m`.`sell_price` AS `sell_price`,(((`trades_15m`.`sell_price` - `trades_15m`.`buy_price`) / `trades_15m`.`sell_price`) * 100) AS `Growth`,`trades_15m`.`total` AS `total`,(`trades_15m`.`buy_price` * `trades_15m`.`total`) AS `total_btc` from `trades_15m` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `growth_1m`
--

/*!50001 DROP TABLE IF EXISTS `growth_1m`*/;
/*!50001 DROP VIEW IF EXISTS `growth_1m`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`greencandle`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `growth_1m` AS select `trades_1m`.`buy_time` AS `buy_time`,`trades_1m`.`sell_time` AS `sell_time`,`trades_1m`.`pair` AS `pair`,`trades_1m`.`buy_price` AS `buy_price`,`trades_1m`.`sell_price` AS `sell_price`,(((`trades_1m`.`sell_price` - `trades_1m`.`buy_price`) / `trades_1m`.`sell_price`) * 100) AS `Growth`,`trades_1m`.`total` AS `total`,(`trades_1m`.`buy_price` * `trades_1m`.`total`) AS `total_btc` from `trades_1m` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `growth_3m`
--

/*!50001 DROP TABLE IF EXISTS `growth_3m`*/;
/*!50001 DROP VIEW IF EXISTS `growth_3m`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`greencandle`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `growth_3m` AS select `trades_3m`.`buy_time` AS `buy_time`,`trades_3m`.`sell_time` AS `sell_time`,`trades_3m`.`pair` AS `pair`,`trades_3m`.`buy_price` AS `buy_price`,`trades_3m`.`sell_price` AS `sell_price`,(((`trades_3m`.`sell_price` - `trades_3m`.`buy_price`) / `trades_3m`.`sell_price`) * 100) AS `Growth`,`trades_3m`.`total` AS `total`,(`trades_3m`.`buy_price` * `trades_3m`.`total`) AS `total_btc` from `trades_3m` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `growth_5m`
--

/*!50001 DROP TABLE IF EXISTS `growth_5m`*/;
/*!50001 DROP VIEW IF EXISTS `growth_5m`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`greencandle`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `growth_5m` AS select `trades_5m`.`buy_time` AS `buy_time`,`trades_5m`.`sell_time` AS `sell_time`,`trades_5m`.`pair` AS `pair`,`trades_5m`.`buy_price` AS `buy_price`,`trades_5m`.`sell_price` AS `sell_price`,(((`trades_5m`.`sell_price` - `trades_5m`.`buy_price`) / `trades_5m`.`sell_price`) * 100) AS `Growth`,`trades_5m`.`total` AS `total`,(`trades_5m`.`buy_price` * `trades_5m`.`total`) AS `total_btc` from `trades_5m` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `hour_balance`
--

/*!50001 DROP TABLE IF EXISTS `hour_balance`*/;
/*!50001 DROP VIEW IF EXISTS `hour_balance`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `hour_balance` AS select `tt1`.`exchange_id` AS `exchange_id`,`tt1`.`usd` AS `usd1`,`tt1`.`coin` AS `coin`,`tt1`.`ctime` AS `ctime1`,`tt2`.`ctime` AS `ctime2`,`tt2`.`usd` AS `usd2`,(`tt1`.`usd` - `tt2`.`usd`) AS `USD_diff`,(`tt1`.`gbp` - `tt2`.`gbp`) AS `GBP_diff`,(`tt1`.`count` - `tt2`.`count`) AS `COUNT_diff`,(((`tt1`.`btc` - `tt2`.`btc`) / `tt1`.`btc`) * 100) AS `perc_change`,(`tt1`.`btc` - `tt2`.`btc`) AS `BTC_diff` from (`balance` `tt1` left join `balance` `tt2` on(((`tt1`.`coin` = `tt2`.`coin`) and (`tt1`.`exchange_id` = `tt2`.`exchange_id`)))) where ((`tt1`.`ctime` > (now() - interval 20 minute)) and (`tt2`.`ctime` < (now() - interval 45 minute)) and (`tt2`.`ctime` > (now() - interval 90 minute))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `profit_15m`
--

/*!50001 DROP TABLE IF EXISTS `profit_15m`*/;
/*!50001 DROP VIEW IF EXISTS `profit_15m`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`greencandle`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `profit_15m` AS select `trades_15m`.`buy_time` AS `buy_time`,`trades_15m`.`sell_time` AS `sell_time`,`trades_15m`.`pair` AS `pair`,(((`trades_15m`.`sell_price` - `trades_15m`.`buy_price`) / `trades_15m`.`sell_price`) * 100) AS `Growth`,`trades_15m`.`total` AS `total`,(`trades_15m`.`buy_price` * `trades_15m`.`total`) AS `total_btc`,((`trades_15m`.`buy_price` * `trades_15m`.`total`) * 5780.38) AS `gbp_buy`,((`trades_15m`.`sell_price` * `trades_15m`.`total`) * 5780.38) AS `gbp_sell`,(((`trades_15m`.`sell_price` * `trades_15m`.`total`) * 5780.38) - ((`trades_15m`.`buy_price` * `trades_15m`.`total`) * 5780.38)) AS `gbp_profit` from `trades_15m` where (`trades_15m`.`sell_price` is not null) order by (((`trades_15m`.`sell_price` * `trades_15m`.`total`) * 5780.38) - ((`trades_15m`.`buy_price` * `trades_15m`.`total`) * 5780.38)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `profit_1m`
--

/*!50001 DROP TABLE IF EXISTS `profit_1m`*/;
/*!50001 DROP VIEW IF EXISTS `profit_1m`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`greencandle`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `profit_1m` AS select `trades_1m`.`buy_time` AS `buy_time`,`trades_1m`.`sell_time` AS `sell_time`,`trades_1m`.`pair` AS `pair`,(((`trades_1m`.`sell_price` - `trades_1m`.`buy_price`) / `trades_1m`.`sell_price`) * 100) AS `Growth`,`trades_1m`.`total` AS `total`,(`trades_1m`.`buy_price` * `trades_1m`.`total`) AS `total_btc`,((`trades_1m`.`buy_price` * `trades_1m`.`total`) * 5780.38) AS `gbp_buy`,((`trades_1m`.`sell_price` * `trades_1m`.`total`) * 5780.38) AS `gbp_sell`,(((`trades_1m`.`sell_price` * `trades_1m`.`total`) * 5780.38) - ((`trades_1m`.`buy_price` * `trades_1m`.`total`) * 5780.38)) AS `gbp_profit` from `trades_1m` where (`trades_1m`.`sell_price` is not null) order by (((`trades_1m`.`sell_price` * `trades_1m`.`total`) * 5780.38) - ((`trades_1m`.`buy_price` * `trades_1m`.`total`) * 5780.38)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `profit_3m`
--

/*!50001 DROP TABLE IF EXISTS `profit_3m`*/;
/*!50001 DROP VIEW IF EXISTS `profit_3m`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`greencandle`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `profit_3m` AS select `trades_3m`.`buy_time` AS `buy_time`,`trades_3m`.`sell_time` AS `sell_time`,`trades_3m`.`pair` AS `pair`,(((`trades_3m`.`sell_price` - `trades_3m`.`buy_price`) / `trades_3m`.`sell_price`) * 100) AS `Growth`,`trades_3m`.`total` AS `total`,(`trades_3m`.`buy_price` * `trades_3m`.`total`) AS `total_btc`,((`trades_3m`.`buy_price` * `trades_3m`.`total`) * 5780.38) AS `gbp_buy`,((`trades_3m`.`sell_price` * `trades_3m`.`total`) * 5780.38) AS `gbp_sell`,(((`trades_3m`.`sell_price` * `trades_3m`.`total`) * 5780.38) - ((`trades_3m`.`buy_price` * `trades_3m`.`total`) * 5780.38)) AS `gbp_profit` from `trades_3m` where (`trades_3m`.`sell_price` is not null) order by (((`trades_3m`.`sell_price` * `trades_3m`.`total`) * 5780.38) - ((`trades_3m`.`buy_price` * `trades_3m`.`total`) * 5780.38)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `profit_5m`
--

/*!50001 DROP TABLE IF EXISTS `profit_5m`*/;
/*!50001 DROP VIEW IF EXISTS `profit_5m`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`greencandle`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `profit_5m` AS select `trades_5m`.`buy_time` AS `buy_time`,`trades_5m`.`sell_time` AS `sell_time`,`trades_5m`.`pair` AS `pair`,(((`trades_5m`.`sell_price` - `trades_5m`.`buy_price`) / `trades_5m`.`sell_price`) * 100) AS `Growth`,`trades_5m`.`total` AS `total`,(`trades_5m`.`buy_price` * `trades_5m`.`total`) AS `total_btc`,((`trades_5m`.`buy_price` * `trades_5m`.`total`) * 5780.38) AS `gbp_buy`,((`trades_5m`.`sell_price` * `trades_5m`.`total`) * 5780.38) AS `gbp_sell`,(((`trades_5m`.`sell_price` * `trades_5m`.`total`) * 5780.38) - ((`trades_5m`.`buy_price` * `trades_5m`.`total`) * 5780.38)) AS `gbp_profit` from `trades_5m` where (`trades_5m`.`sell_price` is not null) order by (((`trades_5m`.`sell_price` * `trades_5m`.`total`) * 5780.38) - ((`trades_5m`.`buy_price` * `trades_5m`.`total`) * 5780.38)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `recent_actions`
--

/*!50001 DROP TABLE IF EXISTS `recent_actions`*/;
/*!50001 DROP VIEW IF EXISTS `recent_actions`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`greencandle`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `recent_actions` AS select `t1`.`id` AS `id`,`t1`.`ctime` AS `ctime`,`t1`.`pair` AS `pair`,`t1`.`indicator` AS `indicator`,`t1`.`value` AS `value`,`t1`.`action` AS `action` from `actions` `t1` where (`t1`.`ctime` = (select max(`t2`.`ctime`) from `actions` `t2` where ((`t2`.`pair` = `t1`.`pair`) and (`t2`.`indicator` = `t2`.`indicator`)))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-04-20 13:53:07
-- MySQL dump 10.16  Distrib 10.1.31-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: greencandle
-- ------------------------------------------------------
-- Server version	10.1.31-MariaDB

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
-- Table structure for table `exchange`
--

DROP TABLE IF EXISTS `exchange`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `exchange` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exchange`
--

LOCK TABLES `exchange` WRITE;
/*!40000 ALTER TABLE `exchange` DISABLE KEYS */;
INSERT INTO `exchange` VALUES (3,'coinbase'),(4,'binance');
/*!40000 ALTER TABLE `exchange` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-04-20 13:53:09
