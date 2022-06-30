import sqlite3

conn = sqlite3.connect('data/website.db')

c = conn.cursor()

c.execute("PRAGMA foreign_keys=1;")

c.execute("""CREATE TABLE Users(
    username TEXT,
    password TEXT,
    user_hash INTEGER PRIMARY KEY
);""")

c.execute("""CREATE TABLE Posts
(
	post_id integer PRIMARY KEY,
	title text,
	content TEXT,
	up integer,
	down integer,
	user_hash integer,
	post_time text,
	user_id text,
	FOREIGN KEY (user_hash) REFERENCES Users(user_hash)
);""")



c.execute("""CREATE TABLE Votes(
    voter integer,
    voted_post_id integer,
    FOREIGN KEY (voter) REFERENCES Users(user_hash)
);""")

conn.commit()

