# 6.29

drop view if exists profit_daily;
create view profit_daily as
select date(close_time), sum(cast(net_perc as decimal(12,2)))  as sum_net_perc, avg(cast(net_perc as decimal(12,2))) as avg_net_perc, max(cast(net_perc as decimal(12,2))) as max_net_perc, min(cast(net_perc as decimal(12,2))) as min_net_perc, count(*) as count,
sum(
  CASE WHEN `net_perc` < 0 THEN
   1
  ELSE
   0
  END) AS `net_loss`,
 sum(
  CASE WHEN `net_perc` > 0 THEN
   1
  ELSE
   0
  END) / count(0) * 100 AS `perc_profitable`,
 sum(
  CASE WHEN `net_perc` > 0 THEN
   1
  ELSE
   0
  END) / count(0) * 100 AS `net_perc_profitable`, sum(cast(usd_net_profit as decimal(12,2))) as usd_net_profit from profit  group by date(close_time) order by date(close_time) desc;

drop view if exists profit_daily_breakdown_close;
drop view if exists profit_daily_breakdown_open;
drop view if exists profit_daily_breakdown;

create view profit_daily_breakdown_close as
select dayname(`profit`.`close_time`) AS `dayname`,`profit`.`interval` AS `interval`,cast(`profit`.`close_time` as date) AS `date`,`profit`.`name` AS `name`,count(0) AS `count`,sum(`profit`.`net_perc`) AS `net_perc`,`profit`.`direction` AS `direction`,sum(case when `profit`.`net_perc` > 0 then 1 else -1 end) / count(0) * 100 AS `net_perc_profitable` from `greencandle`.`profit` group by `profit`.`name`,`profit`.`direction`,cast(`profit`.`close_time` as date) order by cast(`profit`.`close_time` as date) desc,sum(`profit`.`net_perc`) desc;

create view profit_daily_breakdown_open as
select dayname(`profit`.`open_time`) AS `dayname`,`profit`.`interval` AS `interval`,cast(`profit`.`open_time` as date) AS `date`,`profit`.`name` AS `name`,count(0) AS `count`,sum(`profit`.`net_perc`) AS `net_perc`,`profit`.`direction` AS `direction`,sum(case when `profit`.`net_perc` > 0 then 1 else -1 end) / count(0) * 100 AS `net_perc_profitable` from `greencandle`.`profit` group by `profit`.`name`,`profit`.`direction`,cast(`profit`.`open_time` as date) order by cast(`profit`.`open_time` as date) desc,sum(`profit`.`net_perc`) desc;


drop view if exists profit_open_trades_summary;
create view profit_open_trades_summary as
select sum(cast(net_perc as decimal(12,2)))  as sum_net_perc, avg(cast(net_perc as decimal(12,2))) as avg_net_perc, max(cast(net_perc as decimal(12,2))) as max_net_perc, min(cast(net_perc as decimal(12,2))) as min_net_perc, count(*) as count,
sum(
  CASE WHEN `net_perc` > 0 THEN
   1
  ELSE
   0
  END) AS `net_profit`,
sum(
  CASE WHEN `net_perc` < 0 THEN
   1
  ELSE
   0
  END) AS `net_loss`,
 sum(
  CASE WHEN `net_perc` > 0 THEN
   1
  ELSE
   0
  END) / count(0) * 100 AS `net_perc_profitable` from open_trades;


drop function if exists FIRST_DAY_OF_WEEK;
DELIMITER ;;
CREATE FUNCTION FIRST_DAY_OF_WEEK(day DATE)
RETURNS DATE DETERMINISTIC
BEGIN
  RETURN SUBDATE(day, WEEKDAY(day));
END;;
DELIMITER ;

DROP VIEW IF EXISTS profit_weekly;
create view profit_weekly as
SELECT
 concat(year(`profit`.`close_time`), '/', week(`profit`.`close_time`)) AS `week_no`,
 FIRST_DAY_OF_WEEK(date(close_time)) as week_commencing,
 count(0) AS count,
 sum(`profit`.`usd_profit`) AS `usd_profit`,
 sum(`profit`.`usd_net_profit`) AS `usd_net_profit`,
 sum(`profit`.`perc`) AS `perc`,
 sum(`profit`.`net_perc`) AS `net_perc`
FROM
 `greencandle`.`profit`
WHERE
 week(`profit`.`close_time`) IS NOT NULL
GROUP BY
 concat(year(`profit`.`close_time`), '/', week(`profit`.`close_time`))
ORDER BY
 year(`profit`.`close_time`)
 DESC,
 week(`profit`.`close_time`)
 DESC;

