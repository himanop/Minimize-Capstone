#We can think of Minimize as the __init__.py file and the other files as modules.
from Minimize import create_app, socketio  # ✅ Correct: Import `create_app()`

app = create_app()
#When we import we are not running the code in the imported file.
#We are just making the code available to the file that is importing it.
import Minimize.routes
import Minimize.models

if __name__ == "__main__":
    app.run("127.0.0.1", port=5000, debug=True)
    socketio.run(app)

