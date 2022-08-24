# 4.0

select `greencandle`.`trades`.`id` AS `id`,dayname(`greencandle`.`trades`.`open_time`) AS `day`,`greencandle`.`trades`.`open_time` AS `open_time`,`greencandle`.`trades`.`interval` AS `interval`,`greencandle`.`trades`.`close_time` AS `close_time`,`greencandle`.`trades`.`pair` AS `pair`,`greencandle`.`trades`.`name` AS `name`,`greencandle`.`trades`.`open_price` AS `open_price`,`greencandle`.`trades`.`close_price` AS `close_price`,`PERC_DIFF`(`greencandle`.`trades`.`direction`,`greencandle`.`trades`.`open_price`,`greencandle`.`trades`.`close_price`) AS `perc`,`PERC_DIFF`(`greencandle`.`trades`.`direction`,`greencandle`.`trades`.`open_price`,`greencandle`.`trades`.`close_price`) - `commission`() AS `net_perc`,case when `greencandle`.`trades`.`direction` = 'long' then `greencandle`.`trades`.`quote_out` - `greencandle`.`trades`.`quote_in` else `greencandle`.`trades`.`quote_in` - `greencandle`.`trades`.`quote_out` end AS `quote_profit`,case when `greencandle`.`trades`.`direction` = 'long' then `greencandle`.`trades`.`quote_out` - `add_percent`(`greencandle`.`trades`.`quote_in`,`commission`()) else `remove_percent`(`greencandle`.`trades`.`quote_in`,`commission`()) - `greencandle`.`trades`.`quote_out` end AS `quote_net_profit`,case when `greencandle`.`trades`.`direction` = 'long' then (`greencandle`.`trades`.`quote_out` - `greencandle`.`trades`.`quote_in`) * `greencandle`.`trades`.`close_usd_rate` else (`greencandle`.`trades`.`quote_in` - `greencandle`.`trades`.`quote_out`) * `greencandle`.`trades`.`close_usd_rate` end AS `usd_profit`,case when `greencandle`.`trades`.`direction` = 'long' then (`greencandle`.`trades`.`quote_out` - `add_percent`(`greencandle`.`trades`.`quote_in`,`commission`())) * `greencandle`.`trades`.`close_usd_rate` else (`remove_percent`(`greencandle`.`trades`.`quote_in`,`commission`()) - `greencandle`.`trades`.`quote_out`) * `greencandle`.`trades`.`close_usd_rate` end AS `usd_net_profit`,`greencandle`.`trades`.`quote_in` AS `quote_in`,`greencandle`.`trades`.`quote_out` AS `quote_out`,`greencandle`.`trades`.`base_in` AS `base_in`,`greencandle`.`trades`.`base_out` AS `base_out`,`greencandle`.`trades`.`drawup_perc` AS `drawup_perc`,`greencandle`.`trades`.`drawdown_perc` AS `drawdown_perc`,`greencandle`.`trades`.`borrowed` AS `borrowed`,`greencandle`.`trades`.`borrowed_usd` AS `borrowed_usd`,`greencandle`.`trades`.`divisor` AS `divisor`,`greencandle`.`trades`.`direction` AS `direction`,`greencandle`.`trades`.`open_usd_rate` AS `open_usd_rate`,`greencandle`.`trades`.`close_usd_rate` AS `close_usd_rate`,`greencandle`.`trades`.`open_gbp_rate` AS `open_gbp_rate`,`greencandle`.`trades`.`close_gbp_rate` AS `close_gbp_rate`,`greencandle`.`trades`.`comm_open` AS `comm_open`,`greencandle`.`trades`.`comm_close` AS `comm_close` from `greencandle`.`trades` where `greencandle`.`trades`.`close_price` is not null and `greencandle`.`trades`.`close_price` <> '';

drop function IF EXISTS ADD_PERCENT;
CREATE FUNCTION `ADD_PERCENT`(amount DOUBLE,perc decimal(10,2)) RETURNS DOUBLE
RETURN IF(amount > 0, amount + (amount*perc/100), amount - (amount*perc/100));

ALTER TABLE trades RENAME multiplier TO divisor;

ALTER TABLE trades MODIFY COLUMN name varchar(40);
ALTER TABLE trades MODIFY COLUMN closed_by varchar(40);

