# 🎌🇸🇦 Anime Database - Arabic Query Examples

Complete examples showing Arabic queries on an anime database.

---

## 🚀 Quick Start

```bash
# 1. Create anime database
python example_anime_database.py

# 2. Update config.yaml
# database:
#   connection_string: "sqlite:///anime.db"

# 3. Run server
python main.py

# 4. Ask questions in Arabic!
```

---

## 📋 Example Queries (English + Arabic)

### **Basic Queries**

#### 1. Show All Anime
**English:** "Show me all anime"
**Arabic:** "أرني جميع الأنمي"

**Generated SQL:**
```sql
SELECT * FROM anime LIMIT 1000
```

**Expected Results:**
```json
{
  "rows": [
    {"id": 1, "title": "Spirited Away", "rating": 8.6, ...},
    {"id": 2, "title": "My Neighbor Totoro", "rating": 8.1, ...},
    ...
  ]
}
```

---

#### 2. List All Studios
**English:** "List all studios"
**Arabic:** "اعرض جميع الاستوديوهات"

**Generated SQL:**
```sql
SELECT * FROM studios LIMIT 1000
```

---

### **Filtering Queries**

#### 3. Anime from Specific Year
**English:** "Show me anime from 2020"
**Arabic:** "أظهر لي الأنمي من عام 2020"

**Generated SQL:**
```sql
SELECT * FROM anime WHERE release_year = 2020 LIMIT 1000
```

---

#### 4. Anime from Studio
**English:** "Show me all anime from Studio Ghibli"
**Arabic:** "أظهر لي جميع الأنمي من استوديو غيبلي"

**Generated SQL:**
```sql
SELECT a.* 
FROM anime a
JOIN studios s ON a.studio_id = s.id
WHERE s.name = 'Studio Ghibli'
LIMIT 1000
```

**Expected Results:**
- Spirited Away
- My Neighbor Totoro

---

#### 5. Completed Anime
**English:** "Show me completed anime"
**Arabic:** "أرني الأنمي المكتملة"

**Generated SQL:**
```sql
SELECT * FROM anime WHERE status = 'Completed' LIMIT 1000
```

---

### **Aggregation Queries**

#### 6. Count Anime
**English:** "How many anime do we have?"
**Arabic:** "كم عدد الأنمي لدينا؟"

**Generated SQL:**
```sql
SELECT COUNT(*) as total_anime FROM anime
```

**Expected Result:** `15`

---

#### 7. Average Rating
**English:** "What is the average rating of all anime?"
**Arabic:** "ما هو متوسط تقييم جميع الأنمي؟"

**Generated SQL:**
```sql
SELECT AVG(rating) as average_rating FROM anime
```

**Expected Result:** `~8.3`

---

#### 8. Count by Studio
**English:** "How many anime has each studio produced?"
**Arabic:** "كم عدد الأنمي التي أنتجها كل استوديو؟"

**Generated SQL:**
```sql
SELECT s.name, COUNT(a.id) as anime_count
FROM studios s
LEFT JOIN anime a ON s.id = a.studio_id
GROUP BY s.name
ORDER BY anime_count DESC
LIMIT 1000
```

---

#### 9. Count by Genre
**English:** "How many anime are in each genre?"
**Arabic:** "كم عدد الأنمي في كل نوع؟"

**Generated SQL:**
```sql
SELECT g.name, COUNT(ag.anime_id) as anime_count
FROM genres g
LEFT JOIN anime_genres ag ON g.id = ag.genre_id
GROUP BY g.name
ORDER BY anime_count DESC
LIMIT 1000
```

---

### **Sorting & Top Queries**

#### 10. Top Rated Anime
**English:** "Show me the top 5 highest rated anime"
**Arabic:** "أظهر لي أفضل 5 أنمي من حيث التقييم"

**Generated SQL:**
```sql
SELECT * FROM anime ORDER BY rating DESC LIMIT 5
```

**Expected Results:**
1. Fullmetal Alchemist: Brotherhood (9.1)
2. Attack on Titan (8.9)
3. Cowboy Bebop (8.9)
4. Steins;Gate (8.8)
5. Demon Slayer (8.7)

---

#### 11. Longest Anime
**English:** "What are the anime with the most episodes?"
**Arabic:** "ما هي الأنمي التي لديها أكثر عدد من الحلقات؟"

**Generated SQL:**
```sql
SELECT title, episodes FROM anime ORDER BY episodes DESC LIMIT 5
```

**Expected Results:**
1. Naruto (220 episodes)
2. Attack on Titan (87 episodes)
3. Fullmetal Alchemist: Brotherhood (64 episodes)

---

#### 12. Newest Anime
**English:** "Show me the most recent anime"
**Arabic:** "أظهر لي أحدث الأنمي"

**Generated SQL:**
```sql
SELECT * FROM anime ORDER BY release_year DESC LIMIT 5
```

---

### **Join Queries**

#### 13. Anime with Studio Names
**English:** "Show me all anime with their studio names"
**Arabic:** "أظهر لي جميع الأنمي مع أسماء الاستوديوهات"

**Generated SQL:**
```sql
SELECT a.title, s.name as studio_name, a.rating
FROM anime a
JOIN studios s ON a.studio_id = s.id
ORDER BY a.rating DESC
LIMIT 1000
```

---

#### 14. Anime with Genres
**English:** "Show me anime titles with their genres"
**Arabic:** "أظهر لي عناوين الأنمي مع أنواعها"

**Generated SQL:**
```sql
SELECT a.title, GROUP_CONCAT(g.name) as genres
FROM anime a
JOIN anime_genres ag ON a.id = ag.anime_id
JOIN genres g ON ag.genre_id = g.id
GROUP BY a.id, a.title
LIMIT 1000
```

---

#### 15. Characters and Their Anime
**English:** "Show me all characters with their anime"
**Arabic:** "أظهر لي جميع الشخصيات مع الأنمي الخاصة بهم"

**Generated SQL:**
```sql
SELECT c.name as character_name, a.title as anime_title
FROM characters c
JOIN character_anime ca ON c.id = ca.character_id
JOIN anime a ON ca.anime_id = a.id
WHERE ca.is_main_character = 1
LIMIT 1000
```

---

### **Complex Queries**

#### 16. Action Anime Only
**English:** "Show me all action anime"
**Arabic:** "أظهر لي جميع أنمي الأكشن"

**Generated SQL:**
```sql
SELECT DISTINCT a.*
FROM anime a
JOIN anime_genres ag ON a.id = ag.anime_id
JOIN genres g ON ag.genre_id = g.id
WHERE g.name = 'Action'
LIMIT 1000
```

---

#### 17. Long Action Anime
**English:** "Show me action anime with more than 20 episodes"
**Arabic:** "أظهر لي أنمي الأكشن التي لديها أكثر من 20 حلقة"

**Generated SQL:**
```sql
SELECT DISTINCT a.*
FROM anime a
JOIN anime_genres ag ON a.id = ag.anime_id
JOIN genres g ON ag.genre_id = g.id
WHERE g.name = 'Action' AND a.episodes > 20
ORDER BY a.rating DESC
LIMIT 1000
```

**Expected Results:**
- Naruto
- Attack on Titan
- Fullmetal Alchemist: Brotherhood

---

#### 18. Recent High-Rated Anime
**English:** "Show me anime from 2015 or newer with rating above 8.5"
**Arabic:** "أظهر لي الأنمي من 2015 أو أحدث بتقييم أعلى من 8.5"

**Generated SQL:**
```sql
SELECT * FROM anime 
WHERE release_year >= 2015 AND rating > 8.5
ORDER BY rating DESC
LIMIT 1000
```

**Expected Results:**
- Attack on Titan (2013, but ongoing)
- Demon Slayer (2019)
- Jujutsu Kaisen (2020)

---

#### 19. Studios with High Ratings
**English:** "Which studios have anime with average rating above 8.5?"
**Arabic:** "ما هي الاستوديوهات التي لديها أنمي بمتوسط تقييم أعلى من 8.5؟"

**Generated SQL:**
```sql
SELECT s.name, AVG(a.rating) as avg_rating, COUNT(a.id) as anime_count
FROM studios s
JOIN anime a ON s.id = a.studio_id
GROUP BY s.name
HAVING avg_rating > 8.5
ORDER BY avg_rating DESC
LIMIT 1000
```

---

#### 20. Multi-Genre Anime
**English:** "Show me anime that have both Action and Fantasy genres"
**Arabic:** "أظهر لي الأنمي التي تحتوي على نوع الأكشن والفانتازيا معاً"

**Generated SQL:**
```sql
SELECT DISTINCT a.*
FROM anime a
JOIN anime_genres ag1 ON a.id = ag1.anime_id
JOIN anime_genres ag2 ON a.id = ag2.anime_id
WHERE ag1.genre_id = 1 AND ag2.genre_id = 5
LIMIT 1000
```

**Expected Results:**
- Attack on Titan
- Demon Slayer
- Fullmetal Alchemist: Brotherhood
- Naruto

---

### **Character Queries**

#### 21. Find Character's Anime
**English:** "Which anime has Eren as a character?"
**Arabic:** "ما هو الأنمي الذي يحتوي على شخصية إيرين؟"

**Generated SQL:**
```sql
SELECT a.title, c.name as character_name
FROM anime a
JOIN character_anime ca ON a.id = ca.anime_id
JOIN characters c ON ca.character_id = c.id
WHERE c.name LIKE '%Eren%'
LIMIT 1000
```

**Expected Result:** Attack on Titan

---

#### 22. Main Characters
**English:** "Show me all main characters"
**Arabic:** "أظهر لي جميع الشخصيات الرئيسية"

**Generated SQL:**
```sql
SELECT c.name, a.title as anime_title
FROM characters c
JOIN character_anime ca ON c.id = ca.character_id
JOIN anime a ON ca.anime_id = a.id
WHERE ca.is_main_character = 1
LIMIT 1000
```

---

### **Studio Analysis**

#### 23. Most Productive Studio
**English:** "Which studio has produced the most anime?"
**Arabic:** "ما هو الاستوديو الذي أنتج أكبر عدد من الأنمي؟"

**Generated SQL:**
```sql
SELECT s.name, COUNT(a.id) as anime_count
FROM studios s
LEFT JOIN anime a ON s.id = a.studio_id
GROUP BY s.name
ORDER BY anime_count DESC
LIMIT 1
```

**Expected Result:** Madhouse (appears most in our sample)

---

#### 24. Highest Rated Studio
**English:** "Which studio has the highest average rating?"
**Arabic:** "ما هو الاستوديو الذي لديه أعلى متوسط تقييم؟"

**Generated SQL:**
```sql
SELECT s.name, AVG(a.rating) as avg_rating
FROM studios s
JOIN anime a ON s.id = a.studio_id
GROUP BY s.name
ORDER BY avg_rating DESC
LIMIT 1
```

---

### **Date-based Queries**

#### 25. Anime by Decade
**English:** "Show me anime from the 2010s"
**Arabic:** "أظهر لي الأنمي من العقد الثاني من القرن الحادي والعشرين"

**Generated SQL:**
```sql
SELECT * FROM anime 
WHERE release_year BETWEEN 2010 AND 2019
ORDER BY release_year, title
LIMIT 1000
```

---

#### 26. Recent Releases
**English:** "What anime were released in the last 5 years?"
**Arabic:** "ما هي الأنمي التي صدرت في آخر 5 سنوات؟"

**Generated SQL:**
```sql
SELECT * FROM anime 
WHERE release_year >= 2019
ORDER BY release_year DESC
LIMIT 1000
```

---

### **Status Queries**

#### 27. Ongoing Anime
**English:** "Show me all ongoing anime"
**Arabic:** "أظهر لي جميع الأنمي المستمرة"

**Generated SQL:**
```sql
SELECT * FROM anime WHERE status = 'Ongoing' LIMIT 1000
```

**Expected Results:**
- Demon Slayer
- One Punch Man
- Sword Art Online
- Jujutsu Kaisen

---

### **Comparison Queries**

#### 28. Compare Studios
**English:** "Compare the number of anime between Madhouse and Bones"
**Arabic:** "قارن عدد الأنمي بين استوديو Madhouse و Bones"

**Generated SQL:**
```sql
SELECT s.name, COUNT(a.id) as anime_count
FROM studios s
LEFT JOIN anime a ON s.id = a.studio_id
WHERE s.name IN ('Madhouse', 'Bones')
GROUP BY s.name
```

---

#### 29. Genre Popularity
**English:** "Which genre has the most anime?"
**Arabic:** "ما هو النوع الذي يحتوي على أكبر عدد من الأنمي؟"

**Generated SQL:**
```sql
SELECT g.name, COUNT(ag.anime_id) as anime_count
FROM genres g
LEFT JOIN anime_genres ag ON g.id = ag.genre_id
GROUP BY g.name
ORDER BY anime_count DESC
LIMIT 1
```

---

## 🎯 Complete Workflow Example

### Scenario: Finding the Best Action Anime in Arabic

```
Step 1: Ask in Arabic
───────────────────
"أظهر لي أفضل أنمي أكشن مع تقييم أعلى من 8.5"
(Show me the best action anime with rating above 8.5)

Step 2: Server Processing
───────────────────────
✓ LLM understands Arabic
✓ Analyzes database schema
✓ Identifies tables: anime, anime_genres, genres
✓ Generates SQL query

Step 3: Generated SQL
──────────────────
SELECT DISTINCT a.title, a.rating, a.episodes
FROM anime a
JOIN anime_genres ag ON a.id = ag.anime_id  
JOIN genres g ON ag.genre_id = g.id
WHERE g.name = 'Action' AND a.rating > 8.5
ORDER BY a.rating DESC
LIMIT 1000

Step 4: Results
───────────
{
  "success": true,
  "rows": [
    {"title": "Fullmetal Alchemist: Brotherhood", "rating": 9.1, "episodes": 64},
    {"title": "Attack on Titan", "rating": 8.9, "episodes": 87},
    {"title": "Steins;Gate", "rating": 8.8, "episodes": 24},
    {"title": "Demon Slayer", "rating": 8.7, "episodes": 26},
    {"title": "Jujutsu Kaisen", "rating": 8.6, "episodes": 24}
  ]
}
```

---

## 💡 Tips for Arabic Queries

### ✅ Best Practices
1. **Use natural Arabic** - Write as you would speak
2. **Be specific** - More details = better SQL
3. **Use Arabic numbers** if preferred: "٥" or "5" both work
4. **Genre names** can be Arabic: "أكشن" or English: "Action"

### 🎯 Arabic Keywords that Work Well
- **عرض** / **أظهر** / **أرني** = Show me
- **قائمة** / **اعرض** = List
- **كم عدد** = How many
- **ما هو** / **ما هي** = What is/are
- **أفضل** = Best / Top
- **أعلى** = Highest
- **أقل** = Lowest
- **أحدث** = Newest / Latest
- **أقدم** = Oldest
- **من** / **في** = From / In
- **مع** = With
- **بدون** = Without

---

## 🚀 Try It Yourself!

```bash
# 1. Setup
python example_anime_database.py
python main.py

# 2. Ask questions in Arabic:
"أظهر لي جميع الأنمي" (Show me all anime)
"ما هو أفضل أنمي؟" (What is the best anime?)
"كم عدد الأنمي المكتملة؟" (How many completed anime?)
"أرني أنمي 2020" (Show me anime from 2020)
```

---

## 🎉 Summary

✅ **Arabic queries work perfectly**
✅ **Anime database (or any database) works automatically**
✅ **Complex queries supported in Arabic**
✅ **Natural language → SQL conversion is seamless**

**The system understands:**
- Any language for queries ✅
- Any database schema ✅
- Any domain (anime, e-commerce, finance, etc.) ✅

---

**استمتع بالاستعلام! (Enjoy querying!)** 🎌🇸🇦

