-- noinspection SqlNoDataSourceInspectionForFile

CREATE TABLE ships (
    id             serial NOT NULL PRIMARY KEY,
    imo_number     text not null unique,
    reg_number     text not null,
    flag           text not null,
    main_name      text not null,
    secondary_name text not null,
    home_port      text not null,
    call_sign      text not null
);

-- CREATE TABLE "topic"
-- (
--     "id"       serial  NOT NULL PRIMARY KEY,
--     "title"    text    NOT NULL,
--     "image_id" integer REFERENCES "image" ("id") NOT NULL
-- );
--
-- CREATE TABLE "user"
-- (
--     "id"   serial NOT NULL PRIMARY KEY,
--     "name" text   NOT NULL
-- );
--
-- CREATE TABLE "topic_user"
-- (
--     "id"       serial  NOT NULL PRIMARY KEY,
--     "role"     text    NOT NULL,
--     "topic_id" integer REFERENCES "topic" ("id") NOT NULL,
--     "user_id"  integer REFERENCES "user" ("id") NOT NULL
-- );
--
-- CREATE TABLE "question"
-- (
--     "id"       serial  NOT NULL PRIMARY KEY,
--     "text"     text    NOT NULL,
--     "topic_id" integer REFERENCES "topic" ("id") NOT NULL
-- );