from flask import Flask, request

import ui_v1
import ui_v2

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # box score screenshots
app.register_blueprint(ui_v2.bp)
app.register_blueprint(ui_v1.bp, url_prefix='/v1')

# Pages that must never be cached
NO_CACHE_ENDPOINTS = {'v1.Upload', 'v2.upload'}


@app.after_request
def cache_headers(response):
    # Stats only change when new data is uploaded, so browsers and CloudFront can keep pages for 5 minutes
    if request.method == 'GET' and response.status_code == 200 and request.endpoint not in NO_CACHE_ENDPOINTS:
        response.headers.setdefault('Cache-Control', 'public, max-age=300')
    else:
        response.headers['Cache-Control'] = 'no-store'
    return response


if __name__ == '__main__':
    app.run()
