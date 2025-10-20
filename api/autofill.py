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

        company_name = result.get('company_name', 'Unknown Company')

        # Check if the result indicates data was successfully found (you might need a more specific check here)
        success = company_name != 'Unknown Company'

        if success:
            msg = f"✅ Success! Data found and Notion has been updated for: {company_name}"
        else:
            msg = f"⚠️ Warning: No data found for the provided ID, or update failed."

        return _respond(success=success, message=msg, debug=result)

    except Exception as e:
        traceback.print_exc()
        return _respond(success=False, message=f"❌ Error: {str(e)}", status=500)


def _respond(success=True, message="", debug=None, status=200):
    if request.headers.get("Accept", "").startswith("text/html"):
        color = "#28a745" if success else "#dc3545"  # Green for success, red for error

        # Determine the main title and status line based on success
        if success:
            title_text = "Notion Autofill Success"
            heading = "Autofill Result: Success"
        else:
            title_text = "Notion Autofill Failure"
            heading = "Autofill Result: Failure"

        html = f"""
        <html>
        <head>
            <meta charset="UTF-8"> <title>{title_text}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 40px;
                    background-color: #f8f9fa;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                }}
                .box {{
                    background: white;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}
                h2 {{
                    color: #343a40;
                    border-bottom: 2px solid #e9ecef;
                    padding-bottom: 10px;
                    margin-top: 0;
                }}
                .status-message {{
                    color: {color};
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 20px;
                }}
                .debug-info {{
                    margin-top: 20px;
                }}
                .debug-info h3 {{
                    color: #6c757d;
                    font-size: 16px;
                    margin-bottom: 10px;
                }}
                pre {{
                    background: #f1f3f5;
                    padding: 15px;
                    border-radius: 6px;
                    overflow-x: auto;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="box">
                    <h2>{heading}</h2>
                    <p class="status-message">{message}</p>
                    {"<div class='debug-info'><h3>Debug Information:</h3><pre>" + str(debug) + "</pre></div>" if debug else ""}
                </div>
            </div>
        </body>
        </html>
        """
        # Specify the charset in the Content-Type header as well for robustness
        return html, status, {"Content-Type": "text/html; charset=utf-8"}
    else:
        # JSON response does not need the explicit header as Flask handles it by default
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
