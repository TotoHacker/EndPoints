create database endpoins;
use endpoins;
create table SysError(
id int auto_increment primary key,
siteUrl varchar(100),
ErrorSiteCode varchar(100)
);

alter table SysError
add dateError date;

Select * from SysError;