# 📚 ReaderSphere

**ReaderSphere** is a social media platform built for book lovers — a space to connect, share, and chat about your favorite reads. Whether you're looking to discuss novels, make friends with similar interests, or explore new book recommendations, ReaderSphere has something for every reader.

---
## 📸 Screenshots


### 🔐 Profile

![Profile Page](artifacts/1.png)
*User profile view and editing (bio, profile pic, DOB).*

### 📚 Book Search

![Book Search](artifacts/3.png)
*Search books using metadata (scraped with BeautifulSoup).*

### 💬 Messaging
![Chat Interface](artifacts/2.png)
*Real-time 1-on-1 messaging using WebSockets.*

---


## 🌟 Features

- 👤 **User Authentication & Profile Creation**  
  Secure login, registration, and profile setup.

- 📚 **Books Section (Metadata Search)**  
  Search for books using online metadata (currently scraped using BeautifulSoup and GoogleAPI).

- 💬 **Real-Time Messaging**  
  1-on-1 messaging using WebSockets for instant communication.

- 🤝 **Friend Requests**  
  Send/receive friend requests, also powered by WebSockets.

- 🔎 **User Search**  
  Search and connect with fellow book lovers by username.

- 📝 **Profile Editing**  
  Update your bio, profile picture, and date of birth.

- 🧑‍🤝‍🧑 **Group Chats** *(in development)*  
  Interest-based group chats to discuss genres, authors, and more.
  
---

### ⚙️ Architecture

ReaderSphere serves **both as a complete web application** *and* **as a backend API layer** — ideal for:

- 🖥️ **Web Frontend**
- 📱 **Mobile apps (Android/iOS)**
- 💻 **Desktop clients**

All essential features (auth, book search, messaging, profile edits, etc.) are exposed via modular API endpoints, making it plug-and-play for other frontends.

---

## 🛠️ Technologies Used

- **Backend:** Flask  
- **Database:** SQLite  
- **Web Scraping:** BeautifulSoup (for fetching book metadata)  
- **WebSockets:** Flask-SocketIO (for real-time messaging & friend system)  
- **Frontend:** HTML/CSS + JS templates  
- **Architecture:**  
  - RESTful API endpoints  
  - Web interface and API-based backend (ideal for mobile/desktop apps)

---

## 📦 Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/2003HARSH/Readersphere.git
   cd Readersphere
    ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Requirements**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the App**

   ```bash
   python app.py
   ```

   The app should now be running at `http://localhost:5000/`

---

## 📌 Roadmap

* ✅ Basic chat functionality
* ✅ Book metadata search
* ✅ User profile management
* 🚧 Group chats based on interest
* 🚧 Book reviews and ratings
* 🚧 Recommendation engine based on reading habits

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 📬 Contact

For suggestions, queries, or collaborations, feel free to reach out.
Made with ☕, frustration, and `websockets` by **Harsh Gupta**

