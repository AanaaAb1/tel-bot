import uvicorn
from app.admin_panel.api import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
