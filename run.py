import uvicorn
from app.main import app

APP_PORT = 8000


def main():
    uvicorn.run(app, host="127.0.0.1", port=APP_PORT)


if __name__ == "__main__":
    main()
