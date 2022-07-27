from application import app
from application.controllers import users_controller, user_item_controller

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
 