DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS game;
DROP TABLE IF EXISTS score;
PRAGMA foreign_keys = ON;


CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  password_hash TEXT NOT NULL
);


CREATE TABLE game (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  active INTEGER NOT NULL,
  active_user INTEGER NOT NULL,
  stage TEXT NOT NULL,
  dice_0 INTEGER NOT NULL,
  dice_1 INTEGER NOT NULL,
  dice_2 INTEGER NOT NULL,
  dice_3 INTEGER NOT NULL,
  dice_4 INTEGER NOT NULL,
  score_id_0 INTEGER,
  score_id_1 INTEGER,
  score_id_2 INTEGER,
  score_id_3 INTEGER,
  score_id_4 INTEGER,
  score_id_5 INTEGER,
  FOREIGN KEY (score_id_0) REFERENCES score (id),
  FOREIGN KEY (score_id_1) REFERENCES score (id),
  FOREIGN KEY (score_id_2) REFERENCES score (id),
  FOREIGN KEY (score_id_3) REFERENCES score (id),
  FOREIGN KEY (score_id_4) REFERENCES score (id),
  FOREIGN KEY (score_id_5) REFERENCES score (id)
);



CREATE TABLE score (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  ones INTEGER NOT NULL,
  twoes INTEGER NOT NULL,
  threes INTEGER NOT NULL,
  fours INTEGER NOT NULL,
  fives INTEGER NOT NULL,
  sixes INTEGER NOT NULL,
  bonus INTEGER NOT NULL,
  upper_total INTEGER NOT NULL,
  max INTEGER NOT NULL,
  min INTEGER NOT NULL,
  middle_total INTEGER NOT NULL,
  poker INTEGER NOT NULL,
  full_house INTEGER NOT NULL,
  small_straight INTEGER NOT NULL,
  large_straight INTEGER NOT NULL,
  yams INTEGER NOT NULL,
  rigole INTEGER NOT NULL,
  lower_total INTEGER NOT NULL,
  global_total INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES score (id)
);
