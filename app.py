from flask import Flask

import ui_v1
import ui_v2

app = Flask(__name__)
app.register_blueprint(ui_v1.bp)
app.register_blueprint(ui_v2.bp, url_prefix='/v2')


if __name__ == '__main__':
    app.run()
