## Zussamenfassung Teil 2

---

### 1. Python (pymongo)
 
``` Python

from pymongo import MongoClient
 
# Verbindung zum lokalen MongoDB-Server herstellen

client = MongoClient("mongodb://localhost:27017/")
 
# Datenbank "school" auswählen

db = client["school"]
 
# Collection "students" auswählen

collection = db["students"]

```
 
### 2. CREATE

Das Einfügen von Dokumenten ist in beiden Sprachen sehr ähnlich.

#### 💻 `mongosh`

``` JavaScript

// Ein einzelnes Dokument einfügen

db.students.insertOne({ name: "Lars", age: 19, grade: 5.5, skills: ["Python", "SQL"] });
 
// Mehrere Dokumente gleichzeitig einfügen

db.students.insertMany([

  { name: "Anna", age: 21, grade: 5.0, skills: ["Java", "MongoDB"] },

  { name: "Max", age: 18, grade: 4.0, skills: ["HTML", "CSS"] },

  { name: "Mia", age: 20, grade: 6.0, skills: ["Python", "C#", "MongoDB"] }

]);

```

#### 🐍 `Python`

``` Python

# Ein einzelnes Dokument einfügen

student_lars = {"name": "Lars", "age": 19, "grade": 5.5, "skills": ["Python", "SQL"]}

collection.insert_one(student_lars)
 
# Mehrere Dokumente einfügen

students_list = [

    {"name": "Anna", "age": 21, "grade": 5.0, "skills": ["Java", "MongoDB"]},

    {"name": "Max", "age": 18, "grade": 4.0, "skills": ["HTML", "CSS"]},

    {"name": "Mia", "age": 20, "grade": 6.0, "skills": ["Python", "C#", "MongoDB"]}

]

collection.insert_many(students_list)

```
 
### 3. READ
 
Die `find()`-Methode ist das Herzstück von MongoDB. Sie nimmt standardmäßig zwei Argumente entgegen:
 
1. **Query/Filter:** Welche Dokumente wollen wir?

2. **Projection:** Welche Felder (Spalten) sollen im Ergebnis angezeigt werden?
 
`db.collection.find( {Filter}, {Projection} )`

#### 3.1 Alle Dokumente abrufen

Wenn der Filter leer ist `{}`, werden alle Dokumente zurückgegeben.

##### 💻 `mongosh`

```JavaScript

db.students.find({});

// Schön formatiert ausgeben:

db.students.find({}).pretty();

```

##### 🐍 `Python`

```Python

# find() gibt in Python einen Cursor zurück, den wir iterieren müssen

for student in collection.find({}):

    print(student)

```

#### 3.2 Einfache Filter

Wir suchen alle Studenten, die genau 20 Jahre alt sind.

##### 💻 `mongosh`

```JavaScript

db.students.find({ age: 20 });

```

##### 🐍 `Python`

```python

for student in collection.find({"age": 20}):

    print(student)

```

#### 3.3 Operatoren

Operatoren beginnen in MongoDB immer mit einem Dollarzeichen `$`. In Python müssen diese als String in Anführungszeichen gesetzt werden.
 
- `$gt` (greater than) / `$gte` (greater than or equal)

- `$lt` (less than) / `$lte` (less than or equal)

- `$ne` (not equal)

- `$in` (in array)
 
**Beispiel: Alle Studenten älter als 19 Jahre.** **`mongosh`**

##### 💻 `mongosh`

```JavaScript

db.students.find({ age: { $gt: 19 } });

```

##### 🐍 `Python`

```Python

for student in collection.find({"age": {"$gt": 19}}):

    print(student)

```
 
**Beispiel: Studenten mit Note 5.0 oder 6.0 (`$in`).** **`mongosh`**

##### 💻 `mongosh`

```JavaScript

db.students.find({ grade: { $in: [5.0, 6.0] } });

```

##### 🐍 `Python`

```Python

for student in collection.find({"grade": {"$in": [5.0, 6.0]}}):

    print(student)

```

#### 3.4 Logische Operatoren

**Beispiel: Studenten, die älter als 19 sind ODER "Python" als Skill haben.** **`mongosh`**

##### 💻 `mongosh`

```JavaScript

db.students.find({

  $or: [

    { age: { $gt: 19 } },

    { skills: "Python" }

  ]

});

```

##### 🐍 `Python`

```Python

query = {

    "$or": [

        {"age": {"$gt": 19}},

        {"skills": "Python"}

    ]

}

for student in collection.find(query):

    print(student)

```

#### 3.5 Arrays durchsuchen

Suchen in Listen/Arrays.
 
**Beispiel: Studenten, die SOWOHL "Python" ALS AUCH "MongoDB" können.** **`mongosh`**

##### 💻 `mongosh`

```JavaScript

db.students.find({ skills: { $all: ["Python", "MongoDB"] } });

```

##### 🐍 `Python`

```Python

for student in collection.find({"skills": {"$all": ["Python", "MongoDB"]}}):

    print(student)

```

#### 3.6 Textsuche & Regex

Suche nach Namen, die mit "M" beginnen. _Achtung: In der Shell nutzt man oft native JS-Regex

`/M.*/`, in Python `$regex`._

##### 💻 `mongosh`

```JavaScript

db.students.find({ name: /^M/ });

```

##### 🐍 `Python`

```Python

for student in collection.find({"name": {"$regex": "^M"}}):

    print(student)

```

#### 3.7 Felder ein-\/ausblenden

Wir wollen nur den Namen und die Note sehen, aber **nicht** die automatisch generierte `_id`. (`1` = anzeigen, `0` = ausblenden).

##### 💻 `mongosh`

```JavaScript

db.students.find({}, { _id: 0, name: 1, grade: 1 });

```

##### 🐍 `Python`

```Python

for student in collection.find({}, {"_id": 0, "name": 1, "grade": 1}):

    print(student)

```

#### 3.8 Sort, Limit & Überspringen

Sehr nützlich für Paginierung (z.B. Top 3 Studenten anzeigen). `1` = aufsteigend (A-Z, 0-9), `-1` = absteigend (Z-A, 9-0).
 
**Beispiel: Die 2 besten Studenten abrufen.** **`mongosh`**

##### 💻 `mongosh`

```JavaScript

db.students.find().sort({ grade: -1 }).limit(2);

```

##### 🐍 `Python`

```Python

# In pymongo muss man sort() etwas anders aufrufen oder als Liste von Tupeln übergeben

top_students = collection.find().sort("grade", -1).limit(2)
 
for student in top_students:

    print(student)

```
 
### 4. UPDATE

Das Ändern von Daten erfordert ebenfalls Filter, gepaart mit Update-Operatoren wie `$set` (Feld setzen/ändern) oder `$inc` (Zahl erhöhen/verringern).

#### 💻 `mongosh`

```JavaScript

// Ändert die Note von Lars auf 6.0

db.students.updateOne(

  { name: "Lars" },

  { $set: { grade: 6.0 } }

);
 
// Gibt allen Studenten, die älter als 18 sind, den neuen Skill "Git"

db.students.updateMany(

  { age: { $gt: 18 } },

  { $push: { skills: "Git" } }

);

```

#### 🐍 `Python`

```Python

# Note aktualisieren

collection.update_one(

    {"name": "Lars"},

    {"$set": {"grade": 6.0}}

)
 
# Allen über 18 den Skill "Git" hinzufügen

collection.update_many(

    {"age": {"$gt": 18}},

    {"$push": {"skills": "Git"}}

)

```
 
### 5. DELETE

Löschen ist endgültig und funktioniert nach dem gleichen Filter-Prinzip wie `find()`.

#### 💻 `mongosh`

```JavaScript

// Löscht den Studenten mit dem Namen Max

db.students.deleteOne({ name: "Max" });
 
// Löscht alle Studenten mit einer Note schlechter als 4.0

db.students.deleteMany({ grade: { $lt: 4.0 } });

```

#### 🐍 `Python`

```Python

# Einen Studenten löschen

collection.delete_one({"name": "Max"})
 
# Mehrere löschen

collection.delete_many({"grade": {"$lt": 4.0}})

```
 
**Tipp für die Praxis:** Bevor du ein `updateMany` oder `deleteMany` in Skripten oder der Shell ausführst, teste den exakt gleichen Filter immer zuerst mit einem `find()`, um sicherzugehen, dass du nicht versehentlich die falschen Dokumente modifizierst/löschst!
 