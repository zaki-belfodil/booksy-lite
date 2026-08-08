
CREATE TABLE owners(
id INTEGER PRIMARY KEY,
FOREIGN KEY (id) REFERENCES users(userid));
CREATE TABLE business(
owner_id INTEGER UNIQUE,
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
FOREIGN KEY (owner_id) REFERENCES users(userid)
);
CREATE TABLE customer(
id INTEGER PRIMARY KEY,
FOREIGN KEY (id) REFERENCES users(userid));
CREATE TABLE IF NOT EXISTS "users"(
    userid INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT NOT NULL,
    hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "service"(
name TEXT NOT NULL,
id INTEGER PRIMARY KEY AUTOINCREMENT,
duration_min INTEGER
, business_id INTEGER,
FOREIGN KEY (business_id) REFERENCES business(id));
CREATE TABLE service_providing (
    service_id INTEGER,
    provider_id INTEGER,

    PRIMARY KEY (service_id, provider_id),

    FOREIGN KEY (service_id) REFERENCES service(id),
    FOREIGN KEY (provider_id) REFERENCES provider(id)
);
CREATE TABLE appointment(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    service_id INTEGER,
    provider_id INTEGER,
    date TEXT NOT NULL,
    status TEXT NOT NULL,
    start_time INTEGER,
    end_time INTEGER, hour INTEGER, min INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customer(id),
    FOREIGN KEY (service_id) REFERENCES service(id),
    FOREIGN KEY (provider_id) REFERENCES provider(id)
);
CREATE TABLE provider(
id INTEGER PRIMARY KEY,
business_id INTEGER,
start_of_work_per_min INTEGER,
end_of_work_per_min INTEGER, is_owner INTEGER DEFAULT 0,
FOREIGN KEY (id) REFERENCES users(userid),
FOREIGN KEY (business_id) REFERENCES business(id)
);
