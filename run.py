# run.py  (project root)

from app.web import create_app  # NEW import

app = create_app()  # build the Flask instance

if __name__ == "__main__":
    app.run(debug=True)
