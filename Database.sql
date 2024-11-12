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
select * from Api_User;
Select * from Api_SysError, Api_User;