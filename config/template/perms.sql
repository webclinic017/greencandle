CREATE USER 'greencandle'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'greencandle'@'%' WITH GRANT OPTION;
SET GLOBAL sql_mode = 'NO_ENGINE_SUBSTITUTION';
SET GLOBAL max_connections = 1000;
