import sqlite3

# Connect to the database
def connect_db():
    return sqlite3.connect('my_concerts.db')

# Create tables
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Create bands table
    cursor.execute('''CREATE TABLE IF NOT EXISTS bands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        hometown TEXT NOT NULL
    )''')

    # Create venues table
    cursor.execute('''CREATE TABLE IF NOT EXISTS venues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        city TEXT NOT NULL
    )''')

    # Create concerts table
    cursor.execute('''CREATE TABLE IF NOT EXISTS concerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        band_id INTEGER,
        venue_id INTEGER,
        date TEXT,
        FOREIGN KEY (band_id) REFERENCES bands(id),
        FOREIGN KEY (venue_id) REFERENCES venues(id)
    )''')

    # Commit changes
    conn.commit()
    conn.close()

def seed_database():
    conn = connect_db()
    cursor = conn.cursor()

    # Insert bands
    cursor.execute("INSERT INTO bands (name, hometown) VALUES ('Sauti Sol', 'Nairobi')")
    cursor.execute("INSERT INTO bands (name, hometown) VALUES ('Elani', 'Nairobi')")
    cursor.execute("INSERT INTO bands (name, hometown) VALUES ('Wakadinali', 'Mombasa')")

    # Insert venues
    cursor.execute("INSERT INTO venues (title, city) VALUES ('Quiver', 'Nairobi')")
    cursor.execute("INSERT INTO venues (title, city) VALUES ('Megacity', 'Kisumu')")
    cursor.execute("INSERT INTO venues (title, city) VALUES ('Tunnel', 'Mombasa')")

    # Insert concerts
    cursor.execute("INSERT INTO concerts (band_id, venue_id, date) VALUES (1, 1, '2025-12-01')")
    cursor.execute("INSERT INTO concerts (band_id, venue_id, date) VALUES (2, 2, '2022-02-14')")
    cursor.execute("INSERT INTO concerts (band_id, venue_id, date) VALUES (1, 3, '2025-04-23')")
    cursor.execute("INSERT INTO concerts (band_id, venue_id, date) VALUES (3, 1, '2025-12-25')")

    conn.commit()
    conn.close()

# Object Relationship Methods
class Concert:
    def __init__(self, concert_id, band_id, venue_id, date):
        self.id = concert_id  
        self.band_id = band_id
        self.venue_id = venue_id
        self.date = date

    @classmethod
    def band(cls, concert_id):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
                SELECT bands.id, bands.name, bands.hometown 
                FROM concerts 
                JOIN bands ON concerts.band_id = bands.id 
                WHERE concerts.id = ?
            ''', (concert_id,))
        band = cursor.fetchone()
        conn.close()
        return band

    @classmethod
    def venue(cls, concert_id):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
                SELECT venues.id, venues.title, venues.city
                FROM concerts
                JOIN venues ON concerts.venue_id = venues.id
                WHERE concerts.id = ?
            ''', (concert_id,))
        venue = cursor.fetchone()
        conn.close()
        return venue
    
    def hometown_show(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT bands.hometown, venues.city
            FROM concerts
            JOIN bands ON concerts.band_id = bands.id
            JOIN venues ON concerts.venue_id = venues.id
            WHERE concerts.id = ?
        ''', (self.id,))
        band_hometown, venue_city = cursor.fetchone()
        conn.close()
        return band_hometown == venue_city
    
    def introduction(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT bands.name, bands.hometown, venues.city
            FROM concerts
            JOIN bands ON concerts.band_id = bands.id
            JOIN venues ON concerts.venue_id = venues.id
            WHERE concerts.id = ?
        ''', (self.id,))
        band_name, band_hometown, venue_city = cursor.fetchone()
        conn.close()
        return f"Hello {venue_city}!!!!! We are {band_name} and we're from {band_hometown}"

class Band:
    @classmethod
    def concerts(cls, band_id):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM concerts 
            WHERE band_id = ?
        ''', (band_id,))
        concerts = cursor.fetchall()
        conn.close()
        return concerts

    @classmethod
    def venues(cls, band_id):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT venues.* 
            FROM concerts
            JOIN venues ON concerts.venue_id = venues.id
            WHERE concerts.band_id = ?
        ''', (band_id,))
        venues = cursor.fetchall()
        conn.close()
        return venues

    @classmethod
    def play_in_venue(cls, band_id, venue_id, date):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO concerts (band_id, venue_id, date) 
            VALUES (?, ?, ?)
        ''', (band_id, venue_id, date))
        conn.commit()
        conn.close()

    @classmethod
    def all_introductions(cls, band_id):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT concerts.id FROM concerts
            WHERE concerts.band_id = ?
        ''', (band_id,))
        concert_ids = cursor.fetchall()
        introductions = []
        for concert_id in concert_ids:
            concert = Concert(concert_id[0], band_id, None, None)  # Create concert object
            introductions.append(concert.introduction())
        conn.close()
        return introductions

    @classmethod
    def most_performances(cls):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT bands.name, COUNT(concerts.id) AS performance_count
            FROM bands
            JOIN concerts ON bands.id = concerts.band_id
            GROUP BY bands.id
            ORDER BY performance_count DESC
            LIMIT 1
        ''')
        result = cursor.fetchone()
        conn.close()
        return result

class Venue:
    @classmethod
    def concerts(cls, venue_id):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM concerts WHERE venue_id = ?', (venue_id,))
        concerts = cursor.fetchall()
        conn.close()
        return concerts

    @classmethod
    def bands(cls, venue_id):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT bands.* FROM concerts
            JOIN bands ON concerts.band_id = bands.id
            WHERE concerts.venue_id = ?
        ''', (venue_id,))
        bands = cursor.fetchall()
        conn.close()
        return bands

    @classmethod
    def concert_on(cls, venue_id, date):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM concerts 
            WHERE venue_id = ? AND date = ?
        ''', (venue_id, date))
        concert = cursor.fetchone()
        conn.close()
        return concert

    @classmethod
    def most_frequent_band(cls, venue_id):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT bands.name, COUNT(concerts.id) AS performance_count
            FROM bands
            JOIN concerts ON bands.id = concerts.band_id
            WHERE concerts.venue_id = ?
            GROUP BY bands.id
            ORDER BY performance_count DESC
            LIMIT 1
        ''', (venue_id,))
        result = cursor.fetchone()
        conn.close()
        return result

# Main script
if __name__ == "__main__":
    create_tables()
    seed_database()