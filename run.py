#We can think of Minimize as the __init__.py file and the other files as modules.
from Minimize import create_app  # ✅ Correct: Import `create_app()`

app = create_app()
from Minimize import routes 
# app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(debug=True)

