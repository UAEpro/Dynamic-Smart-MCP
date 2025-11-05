"""
Anime Database Creator
Creates a sample anime database to demonstrate Smart MCP Server capabilities.
"""

import sqlite3
from datetime import datetime

def create_anime_database(db_path: str = "anime.db"):
    """Create a sample anime database with realistic data."""
    
    print(f"Creating anime database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Drop existing tables
    c.execute("DROP TABLE IF EXISTS character_anime")
    c.execute("DROP TABLE IF EXISTS characters")
    c.execute("DROP TABLE IF EXISTS anime_genres")
    c.execute("DROP TABLE IF EXISTS genres")
    c.execute("DROP TABLE IF EXISTS episodes")
    c.execute("DROP TABLE IF EXISTS anime")
    c.execute("DROP TABLE IF EXISTS studios")
    
    # Create studios table
    c.execute('''CREATE TABLE studios (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        founded_year INTEGER,
        country TEXT
    )''')
    
    # Create genres table
    c.execute('''CREATE TABLE genres (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        description TEXT
    )''')
    
    # Create anime table
    c.execute('''CREATE TABLE anime (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        title_japanese TEXT,
        studio_id INTEGER,
        episodes INTEGER,
        rating REAL,
        release_year INTEGER,
        status TEXT,
        synopsis TEXT,
        FOREIGN KEY (studio_id) REFERENCES studios(id)
    )''')
    
    # Create anime_genres junction table
    c.execute('''CREATE TABLE anime_genres (
        anime_id INTEGER,
        genre_id INTEGER,
        PRIMARY KEY (anime_id, genre_id),
        FOREIGN KEY (anime_id) REFERENCES anime(id),
        FOREIGN KEY (genre_id) REFERENCES genres(id)
    )''')
    
    # Create characters table
    c.execute('''CREATE TABLE characters (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        name_japanese TEXT,
        age INTEGER,
        role TEXT
    )''')
    
    # Create character_anime junction table
    c.execute('''CREATE TABLE character_anime (
        character_id INTEGER,
        anime_id INTEGER,
        is_main_character INTEGER DEFAULT 0,
        PRIMARY KEY (character_id, anime_id),
        FOREIGN KEY (character_id) REFERENCES characters(id),
        FOREIGN KEY (anime_id) REFERENCES anime(id)
    )''')
    
    # Insert studios
    studios = [
        (1, "Studio Ghibli", 1985, "Japan"),
        (2, "Kyoto Animation", 1981, "Japan"),
        (3, "Madhouse", 1972, "Japan"),
        (4, "Bones", 1998, "Japan"),
        (5, "Ufotable", 2000, "Japan"),
        (6, "A-1 Pictures", 2005, "Japan"),
        (7, "Trigger", 2011, "Japan")
    ]
    c.executemany("INSERT INTO studios VALUES (?, ?, ?, ?)", studios)
    
    # Insert genres
    genres = [
        (1, "Action", "Fast-paced with combat and battles"),
        (2, "Adventure", "Journey and exploration"),
        (3, "Comedy", "Humorous and lighthearted"),
        (4, "Drama", "Emotional and character-driven"),
        (5, "Fantasy", "Magical and supernatural elements"),
        (6, "Romance", "Love stories and relationships"),
        (7, "Sci-Fi", "Science fiction and futuristic"),
        (8, "Slice of Life", "Everyday life and activities"),
        (9, "Thriller", "Suspense and mystery"),
        (10, "Supernatural", "Paranormal and mystical")
    ]
    c.executemany("INSERT INTO genres VALUES (?, ?, ?)", genres)
    
    # Insert anime
    anime_list = [
        (1, "Spirited Away", "千と千尋の神隠し", 1, 1, 8.6, 2001, "Completed", 
         "A young girl enters a magical world while trying to save her parents."),
        (2, "My Neighbor Totoro", "となりのトトロ", 1, 1, 8.1, 1988, "Completed",
         "Two sisters discover magical creatures in the countryside."),
        (3, "Attack on Titan", "進撃の巨人", 3, 87, 8.9, 2013, "Completed",
         "Humanity fights for survival against giant humanoid Titans."),
        (4, "Demon Slayer", "鬼滅の刃", 5, 26, 8.7, 2019, "Ongoing",
         "A boy becomes a demon slayer to save his sister and avenge his family."),
        (5, "Your Name", "君の名は", 4, 1, 8.4, 2016, "Completed",
         "Two teenagers mysteriously swap bodies and fall in love."),
        (6, "Fullmetal Alchemist: Brotherhood", "鋼の錬金術師", 4, 64, 9.1, 2009, "Completed",
         "Two brothers search for the Philosopher's Stone to restore their bodies."),
        (7, "Death Note", "デスノート", 3, 37, 8.6, 2006, "Completed",
         "A student discovers a notebook that can kill anyone whose name is written in it."),
        (8, "Steins;Gate", "シュタインズ・ゲート", 3, 24, 8.8, 2011, "Completed",
         "A group of friends accidentally invents time travel."),
        (9, "One Punch Man", "ワンパンマン", 3, 24, 8.5, 2015, "Ongoing",
         "A hero who can defeat any opponent with a single punch seeks a worthy challenge."),
        (10, "Violet Evergarden", "ヴァイオレット・エヴァーガーデン", 2, 13, 8.4, 2018, "Completed",
         "A former soldier learns the meaning of love through writing letters."),
        (11, "Naruto", "ナルト", 3, 220, 8.3, 2002, "Completed",
         "A young ninja seeks recognition and dreams of becoming the Hokage."),
        (12, "Cowboy Bebop", "カウボーイビバップ", 3, 26, 8.9, 1998, "Completed",
         "A group of bounty hunters travel through space seeking criminals."),
        (13, "Sword Art Online", "ソードアート・オンライン", 6, 25, 7.6, 2012, "Ongoing",
         "Players trapped in a virtual reality MMORPG must complete the game to escape."),
        (14, "Kill la Kill", "キルラキル", 7, 24, 8.0, 2013, "Completed",
         "A girl seeks her father's killer at a school ruled by special uniforms."),
        (15, "Jujutsu Kaisen", "呪術廻戦", 3, 24, 8.6, 2020, "Ongoing",
         "A high school student joins a secret organization to fight cursed spirits.")
    ]
    c.executemany("INSERT INTO anime VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", anime_list)
    
    # Insert anime-genre relationships
    anime_genres = [
        # Spirited Away
        (1, 2), (1, 5),
        # Totoro
        (2, 2), (2, 5),
        # Attack on Titan
        (3, 1), (3, 4), (3, 5),
        # Demon Slayer
        (4, 1), (4, 2), (4, 5), (4, 10),
        # Your Name
        (5, 4), (5, 6), (5, 10),
        # FMA Brotherhood
        (6, 1), (6, 2), (6, 4), (6, 5),
        # Death Note
        (7, 9), (7, 10),
        # Steins;Gate
        (8, 7), (8, 9), (8, 4),
        # One Punch Man
        (9, 1), (9, 3), (9, 7),
        # Violet Evergarden
        (10, 4), (10, 5),
        # Naruto
        (11, 1), (11, 2), (11, 5),
        # Cowboy Bebop
        (12, 1), (12, 7), (12, 4),
        # SAO
        (13, 1), (13, 2), (13, 6), (13, 7),
        # Kill la Kill
        (14, 1), (14, 3),
        # Jujutsu Kaisen
        (15, 1), (15, 4), (15, 10)
    ]
    c.executemany("INSERT INTO anime_genres VALUES (?, ?)", anime_genres)
    
    # Insert characters
    characters = [
        (1, "Chihiro Ogino", "荻野 千尋", 10, "Protagonist"),
        (2, "Totoro", "トトロ", None, "Spirit"),
        (3, "Eren Yeager", "エレン・イェーガー", 19, "Protagonist"),
        (4, "Tanjiro Kamado", "竈門 炭治郎", 15, "Protagonist"),
        (5, "Mitsuha Miyamizu", "宮水 三葉", 17, "Protagonist"),
        (6, "Edward Elric", "エドワード・エルリック", 17, "Protagonist"),
        (7, "Light Yagami", "夜神月", 17, "Protagonist"),
        (8, "Okabe Rintarou", "岡部倫太郎", 18, "Protagonist"),
        (9, "Saitama", "サイタマ", 25, "Protagonist"),
        (10, "Violet Evergarden", "ヴァイオレット", 14, "Protagonist"),
        (11, "Naruto Uzumaki", "うずまきナルト", 16, "Protagonist"),
        (12, "Spike Spiegel", "スパイク・スピーゲル", 27, "Protagonist"),
        (13, "Mikasa Ackerman", "ミカサ・アッカーマン", 19, "Deuteragonist"),
        (14, "Nezuko Kamado", "竈門 禰豆子", 14, "Deuteragonist"),
        (15, "Alphonse Elric", "アルフォンス・エルリック", 14, "Deuteragonist")
    ]
    c.executemany("INSERT INTO characters VALUES (?, ?, ?, ?, ?)", characters)
    
    # Link characters to anime
    character_anime = [
        (1, 1, 1), (2, 2, 1), (3, 3, 1), (4, 4, 1), (5, 5, 1),
        (6, 6, 1), (7, 7, 1), (8, 8, 1), (9, 9, 1), (10, 10, 1),
        (11, 11, 1), (12, 12, 1), (13, 3, 1), (14, 4, 1), (15, 6, 1)
    ]
    c.executemany("INSERT INTO character_anime VALUES (?, ?, ?)", character_anime)
    
    conn.commit()
    conn.close()
    
    print("✅ Anime database created successfully!")
    print(f"   - {len(studios)} studios")
    print(f"   - {len(genres)} genres")
    print(f"   - {len(anime_list)} anime titles")
    print(f"   - {len(characters)} characters")
    print()
    print("Now you can ask questions like:")
    print('   🇺🇸 English: "Show me all action anime from 2013"')
    print('   🇸🇦 Arabic: "أظهر لي أفضل الأنمي تقييماً" (Show me the highest rated anime)')
    print('   🇫🇷 French: "Quels sont les anime de Studio Ghibli?"')
    print('   🇯🇵 Japanese: "進撃の巨人のキャラクターを表示して" (Show Attack on Titan characters)')
    print()
    print('Update config.yaml:')
    print('   database:')
    print('     connection_string: "sqlite:///anime.db"')


if __name__ == "__main__":
    create_anime_database()

