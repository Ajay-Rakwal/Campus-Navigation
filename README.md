# 🏫 Campus Navigator Mini Project

A smart **Campus Navigation and Route Optimization System** built using **Python**, **MySQL**, and classic **graph algorithms (A\*, Dijkstra, and Kruskal’s MST)**.  
The project provides a full-featured **Tkinter GUI** to visualize buildings, routes, and reachability — helping users find the **shortest path**, explore **within a distance limit**, and understand **minimal campus connectivity**.

---

## 🧩 Features

✅ **Implements A\* Search** to find the shortest path between two locations  
✅ **Kruskal’s Algorithm (MST)** to find minimal infrastructure connections  
✅ **Dijkstra’s Algorithm (SPT)** for distance-based reachability (within budget)  
✅ **MySQL Integration** for login/signup and saving route history  
✅ **Interactive Tkinter GUI** with campus map, arrows, and color-coded visualization  
✅ **Full-window scrolling**, auto-sized nodes, and clean modern design  
✅ **Persistent route history** with timestamps in a scrollable list  

---

## 🗂️ Project Structure

```
Campus-Navigator/
│
├── main.py               # Entry point of the project (contains full code)
├── README.md             # Project documentation (this file)
├── requirements.txt      # Python dependencies
├── screenshots/          # (optional) GUI screenshots
└── LICENSE               # Open-source license (MIT)
```

---

## 🧠 Technologies Used

| Component | Technology |
|------------|-------------|
| **Programming Language** | Python 3.10+ |
| **Database** | MySQL |
| **Libraries** | tkinter, mysql-connector-python, heapq |
| **Algorithms Used** | A\* (AI), Dijkstra’s (DAA), Kruskal’s MST (DAA) |
| **IDE** | VS Code / PyCharm |
| **Operating System** | Windows 10+ / Linux |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Ajay-Rakwal/Campus-Navigator.git
cd Campus-Navigator
```

### 2️⃣ Install Required Libraries
Make sure Python 3.8+ is installed. Then run:
```bash
pip install mysql-connector-python
```

### 3️⃣ Setup MySQL Database
Open your MySQL shell or GUI (like phpMyAdmin or MySQL Workbench) and run:

```sql
CREATE DATABASE campus_navigator;

USE campus_navigator;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE,
  password VARCHAR(50)
);

CREATE TABLE saved_routes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50),
  source VARCHAR(50),
  destination VARCHAR(50),
  route_text TEXT,
  saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4️⃣ Configure Database Connection
In the `connect_db()` function inside `main.py`, update your MySQL credentials:
```python
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_mysql_password",
        database="campus_navigator"
    )
```

### 5️⃣ Run the Project
```bash
python main.py
```

---

## 🧮 Functional Overview

### 🔹 Find Path (A\* Algorithm)
- Finds the **shortest path** between any two buildings.  
- Displays the path visually with **direction arrows (blue)**.  
- Shows total distance and allows saving the route to the database.

### 🔹 Show MST (Kruskal’s Algorithm)
- Generates a **Minimum Spanning Tree** connecting all buildings with minimum total cost.  
- Highlights the MST edges in **green** and lists them with total weight.

### 🔹 Within Budget (Dijkstra’s Algorithm)
- User specifies a **budget distance** and a **starting point**.  
- The program highlights all nodes reachable within that budget.  
- Displays these reachable buildings (yellow) and the shortest path tree (orange edges).

### 🔹 SQL Integration
- Stores user credentials and route history.
- “View Saved Routes” button displays all previously saved routes in a scrollable window.

---

## 🧠 Concepts Applied

| Subject | Concepts Used |
|----------|----------------|
| **Python** | Tkinter GUI, classes, OOP, canvas drawing |
| **SQL** | Database connection, CRUD operations |
| **DAA** | Kruskal’s MST, Dijkstra’s SPT |
| **AI** | A\* heuristic search (for shortest path) |
| **Software Design** | Modular code, event-driven programming, MVC separation |

---

## 🚀 Future Enhancements
- Add heuristic function (straight-line distance) to improve A\* efficiency  
- Add “Avoid road” or “Closed route” simulation  
- Add admin mode to edit campus map  
- Export saved routes as PDF  
- Introduce live path animation and dark mode  

---

## 🧾 Author

👨‍💻 **Ajay Rakwal**  
🎓 MCA (AI & ML), Chandigarh University  
📅 Project Duration: November 2025  
📫 Email: ajayrakwal@example.com  
🔗 GitHub: [Ajay-Rakwal](https://github.com/Ajay-Rakwal)

---

## 📜 License

This project is created for academic and educational purposes.  
You are free to use, modify, and distribute it with proper credit to the author.

---

## ⭐ Show Some Support!
If you found this project helpful, don’t forget to star ⭐ this repository on GitHub!
