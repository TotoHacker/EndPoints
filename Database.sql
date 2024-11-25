/*create database endpoins;
use endpoins;
create table SysError(
id int auto_increment primary key,
siteUrl varchar(100),
ErrorSiteCode varchar(100)
);

alter table SysError
add dateError date;

Select * from SysError;

Create table User(
id int auto_increment primary key,
NameUser varchar(100),
email varchar (100),
passwordUser varchar(100)
);
*/
use endpoins;
select * from auth_user;
select * from Api_User;
Select * from Api_SettingsMonitor ;
INSERT INTO `endpoins`.`auth_user` 
(`password`, `last_login`, `username`, `first_name`, `last_name`, `email`, `is_active`, `is_superuser`, `is_staff`) 
VALUES 
('12345', '2024-11-25 10:00:00', 'luis', 'lui', 'ba', 'toto@toto.com', '1', '0', '0');


