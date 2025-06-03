# Faketify Server

The **Faketify Server** is the backend API for the Faketify hoax detection system. It connects the client-facing application with the machine learning model layer to provide real-time hoax classification of political news headlines.

## ⚙️ Tech Stack

- **FastAPI** – Web framework for building the API  
- **Pydantic** – Data validation and serialization  
- **SQLAlchemy** – ORM for handling database operations  
- **PostgreSQL / SQLite** – Database support  
- **Python** 3.9.2  

## 📦 Features

- RESTful API for submitting headlines and receiving predictions  
- JSON-based input/output  
- Stores prediction history in a database  
- Accepts user feedback on predictions  


## 🚀 Running the Server

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the FastAPI server:

```bash
fastapi dev ./app/main.py --reload
```

## 📚 Available Endpoints

| Method | Endpoint            | Description                            |
|--------|---------------------|----------------------------------------|
| POST   | `/detect`           | Submit a headline for hoax detection   |
| GET    | `/detection`        | Get paginated detection history        |
| GET    | `/detection/{id}`   | Get specific detection + feedback      |
| POST   | `/feedback`         | Submit user feedback on a prediction   |

You can also check on /docs to see detailed explanation of the endpoints

## 📝 Environment Variables

You can use a `.env` file for custom config:

```
DATABASE_URL=sqlite:///./faketify.db
MODEL_LAYER_URL=http://localhost:8001/predict
```


## 🙏 Acknowledgments

Part of the undergraduate thesis project at Universitas Hasanuddin:  
**"Sistem Deteksi Hoaks dengan Mempertimbangkan Fitur Temporal (Studi Kasus: Pemilu Amerika Serikat 2024)"**






