# clear the data
drop table if exists entries;
drop table if exists users;

# creating tables
create table entries (
  id integer primary key autoincrement,
  title text not null,
  text text not null
);

create table users (
  id integer primary key autoincrement,
  login text not null,
  fullname text not null,
  email text not null,
  password text not null
);

# init data
insert into users VALUES ('admin', 'administrator', 'cospelthetraceur@gmail.com', 'admin')