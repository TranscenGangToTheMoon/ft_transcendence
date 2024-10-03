CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    nickname VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE,
    password TEXT,
    created_at TIMESTAMP DEFAULT current_timestamp,
    last_online TIMESTAMP
);

CREATE TABLE matches(
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP,
    finish_at TIMESTAMP DEFAULT current_timestamp,
    id_player1 INT,
    score_player1 INT,
    id_player2 INT,
    score_player2 INT,
    winner_id INT,
    FOREIGN KEY(id_player1) REFERENCES "user"(id),
    FOREIGN KEY(id_player2) REFERENCES "user"(id),
    FOREIGN KEY(winner_id) REFERENCES "user"(id),
);

SELECT * FROM match JOIN "user" u ON u.id = match.id_player1 OR u.id match.id_player2;