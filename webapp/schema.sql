-- clear the data
drop table if exists entries;
drop table if exists users;

-- creating tables
create table entries (
  id integer primary key autoincrement,
  title text not null,
  text text not null,
  city text not null,
  address text not null,
);

create table users (
  login text primary key,
  fullname text not null,
  email text not null,
  password text not null
);

-- init data
insert into users (login, fullname, email, password) VALUES ('admin', 'administrator', 'cospelthetraceur@gmail.com', 'admin')