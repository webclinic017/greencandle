# 4.7

drop view if exists profitable_by_name;
create view profitable_by_name as select `profit`.`name` AS `name`,count(0) AS `total`,sum(case when `profit`.`perc` > 0 then 1 else 0 end) AS `profit`,sum(case when `profit`.`net_perc` > 0 then 1 else 0 end) AS `net_profit`,sum(case when `profit`.`net_perc` < 0 then 1 else 0 end) AS `net_loss`,sum(case when `profit`.`perc` > 0 then 1 else 0 end) / count(0) * 100 AS `perc_profitable`,sum(case when `profit`.`net_perc` > 0 then 1 else 0 end) / count(0) * 100 AS `net_perc_profitable`,sum(`profit`.`perc`) AS `total_perc`,sum(`profit`.`perc`) / count(0) AS `per_trade`,sum(`profit`.`net_perc`) AS `total_net_perc`,sum(`profit`.`net_perc`) / count(0) AS `net_per_trade`,max(`profit`.`perc`) AS `max(perc)`,min(`profit`.`perc`) AS `min(perc)`,max(`profit`.`net_perc`) AS `max(net_perc)`,min(`profit`.`net_perc`) AS `min(net_perc)` from `greencandle`.`profit` group by `profit`.`name` order by sum(case when `profit`.`perc` > 0 then 1 else 0 end) / count(0) * 100 desc;

drop view if exists profitable_by_name_date;
create view profitable_by_name_date as select `profit`.`name` AS `name`, date(open_time) as `date`, count(0) AS `total`,sum(case when `profit`.`perc` > 0 then 1 else 0 end) AS `profit`,sum(case when `profit`.`net_perc` > 0 then 1 else 0 end) AS `net_profit`,sum(case when `profit`.`net_perc` < 0 then 1 else 0 end) AS `net_loss`,sum(case when `profit`.`perc` > 0 then 1 else 0 end) / count(0) * 100 AS `perc_profitable`,sum(case when `profit`.`net_perc` > 0 then 1 else 0 end) / count(0) * 100 AS `net_perc_profitable`,sum(`profit`.`perc`) AS `total_perc`,sum(`profit`.`perc`) / count(0) AS `per_trade`,sum(`profit`.`net_perc`) AS `total_net_perc`,sum(`profit`.`net_perc`) / count(0) AS `net_per_trade`,max(`profit`.`perc`) AS `max(perc)`,min(`profit`.`perc`) AS `min(perc)`,max(`profit`.`net_perc`) AS `max(net_perc)`,min(`profit`.`net_perc`) AS `min(net_perc)` from `greencandle`.`profit` group by `profit`.`name`, date(open_time) order by date(open_time) desc;


ALTER TABLE trades MODIFY base_out varchar(40);
ALTER TABLE trades MODIFY base_in varchar(40);
ALTER TABLE trades MODIFY quote_out varchar(40);
ALTER TABLE trades MODIFY quote_in varchar(40);
ALTER TABLE open_trades MODIFY usd_quantity varchar(40);

