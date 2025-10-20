from flask import Flask, request, jsonify
import os
import traceback

# Use relative imports to find files in the same directory.
from .sync import autofill_page_by_page_id

app = Flask(__name__)


# This is the route that will be triggered by your Notion button.
@app.route('/api/autofill', methods=['GET', 'POST'])
def autofill():
    try:
        # Get pageId from query parameters or JSON body
        if request.method == 'GET':
            page_id = request.args.get('pageId')
        else:  # POST
            data = request.get_json() or {}
            page_id = data.get('pageId') or request.args.get('pageId')

        if not page_id:
            return jsonify({"error": "No pageId provided"}), 400

        # Run autofill. The function will get its own config from env variables.
        result = autofill_page_by_page_id(page_id)

        msg = f"✅ Data found and Notion has been updated: {result.get('company_name', 'Tundmatu ettevõte')}"
        return _respond(success=True, message=msg, debug=result)


    except Exception as e:

        traceback.print_exc()

        return _respond(success=False, message=f"⚠️ Error: {str(e)}", status=500)


def _respond(success=True, message="", debug=None, status=200):
    if request.headers.get("Accept", "").startswith("text/html"):
        color = "#28a745" if success else "#dc3545"
        html = f"""
        <html>
        <head>
            <title>Notion Autofill</title>
            <style>
                body {{
                    font-family: sans-serif;
                    margin: 40px;
                    background-color: #f8f9fa;
                }}
                .box {{
                    background: white;
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                }}
                .status {{
                    color: {color};
                    font-size: 20px;
                }}
                pre {{
                    background: #f1f3f5;
                    padding: 10px;
                    border-radius: 6px;
                }}
            </style>
        </head>
        <body>
            <div class="box">
                <h2>Notion Autofill tulemus</h2>
                <p class="status">{message}</p>
                {"<pre>" + str(debug) + "</pre>" if debug else ""}
            </div>
        </body>
        </html>
        """
        return html, status, {"Content-Type": "text/html"}
    else:
        return jsonify({
            "success": success,
            "message": message,
            "debug": debug
        }), status


# A simple health check to confirm the server is running.
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Notion Autofill API is running",
    })


# For local development
if __name__ == "__main__":
    print("Starting Flask API on http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
