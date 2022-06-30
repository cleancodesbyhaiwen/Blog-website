PRAGMA foreign_keys=1;

CREATE TABLE Users(
    first_name TEXT,
    last_name TEXT,
    user_id TEXT,
    password TEXT,
    user_hash INTEGER PRIMARY KEY
);

CREATE TABLE Posts
(   post_id integer PRIMARY KEY,
	title text,
	content TEXT,
	up integer,
	down integer,
	user_hash integer,
	post_time text,
	user_id text,
	FOREIGN KEY (user_hash) REFERENCES Users(user_hash)
);

CREATE TABLE Votes(
    voter integer,
    voted_post_id integer,
    FOREIGN KEY (voter) REFERENCES Users(user_hash)
);

CREATE TRIGGER delete_account AFTER DELETE ON Users
BEGIN
    DELETE FROM Posts WHERE user_hash=old.user_hash;
END;
