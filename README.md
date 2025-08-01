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
*Real-time 1-on-1 messaging using WebSockets.*### 💬 Messaging

### 💬 Groups

![Chat Interface](artifacts/4.png)
*Create a space with like minded readers.*

---

## 🌟 Features

* 👤 **User Authentication & Profile Creation**
  Secure login, registration, and profile setup.

* 📚 **Books Section (Metadata Search)**
  Search for books using online metadata (scraped via BeautifulSoup + Google API).

* 💬 **Real-Time Messaging**
  1-on-1 messaging using WebSockets for instant communication.

* 🤝 **Friend Requests**
  Send/receive friend requests, also powered by WebSockets.

* 🔎 **User Search**
  Search and connect with fellow book lovers by username.

* 📝 **Profile Editing**
  Update your bio, profile picture, and date of birth.

* ☁️ **Cloud Storage (S3)**
  Profile pictures are stored on **AWS S3** for reliability and performance.

* 👥 **Group Chats (NEW!)**
  Users can **create groups** and **add their friends** to spark conversations around shared interests, genres, or favorite authors — a virtual reading room for like-minded readers.

---

## ⚙️ Architecture & Deployment

ReaderSphere is designed with a modular architecture and is deployed using **Render**, with AWS for media storage.

### 🧱 Application Architecture

* Flask-based **REST API** backend
* Templated **HTML/CSS/JS frontend** (Jinja2)
* **WebSocket** support via Flask-SocketIO
* **BeautifulSoup** + Google Books API for book metadata scraping

### 🚀 Deployment

* **Render**: Hosts the full-stack web app
* **Free PostgreSQL Hosting**: For persistent storage of user data, messages, groups, etc.
* **AWS S3**: For profile picture and media storage
* **GitHub Actions**: CI/CD pipeline for automatic deployment

---

## 🛠️ Technologies Used

| Category           | Tech Stack                                           |
| ------------------ | ---------------------------------------------------- |
| **Backend**        | Flask, Flask-SocketIO, RESTful APIs                  |
| **Frontend**       | HTML/CSS, JavaScript, Jinja2 Templates               |
| **Database**       | PostgreSQL (Free cloud DB provider)                  |
| **Web Scraping**   | BeautifulSoup, Google Books API                      |
| **Cloud Platform** | **Render** (App Hosting), **AWS S3** (Media Storage) |
| **CI/CD**          | GitHub Actions                                       |

---

## 📦 Local Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/2003HARSH/Readersphere.git
   cd Readersphere
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the App**

   ```bash
   python app.py
   ```

   The app will be live at: `http://localhost:5000/`

---

## 📌 Roadmap

* ✅ Real-time 1-on-1 chat
* ✅ Book metadata scraping + search
* ✅ User profile creation and editing
* ✅ Group chat creation and management
* ✅ Render + S3 deployment
* 🚧 Book reviews and ratings
* 🚧 Personalized book recommendation engine
* 🚧 Mobile-first responsive redesign

---

## 🤝 Contributing

Pull requests are welcome! For major changes, open an issue first to discuss what you’d like to improve or add.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 📬 Contact

For suggestions, queries, or collaborations, feel free to reach out.

Made with ☕, frustration, and `websockets` by **Harsh Gupta**
GitHub: [@2003HARSH](https://github.com/2003HARSH)
