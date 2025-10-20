from flask import Flask, jsonify
import os
from .notion_client import NotionClient
from .sync import autofill_page_by_page_id

app = Flask(__name__)

@app.route('/api/watcher', methods=['GET'])
def watcher():
    """
    This function is triggered by a Vercel Cron Job.
    It queries the Notion database for pages with a 'Processing' status,
    then triggers the autofill logic for each one.
    """
    NOTION_API_KEY = os.getenv("NOTION_API_KEY")
    NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

    if not all([NOTION_API_KEY, NOTION_DATABASE_ID]):
        return jsonify({"error": "Missing Notion environment variables"}), 500

    notion = NotionClient(NOTION_API_KEY, NOTION_DATABASE_ID)
    
    try:
        pages_to_process = notion.query_by_status("ja")
        
        if not pages_to_process:
            return jsonify({"status": "ok", "message": "No pages to process."}), 200

        for page in pages_to_process:
            page_id = page["id"]
            print(f"Processing page: {page_id}")
            try:
                autofill_page_by_page_id(page_id)
            except Exception as e:
                print(f"Error processing page {page_id}: {e}")
                # Optionally, update the page status to 'Error' here
                
        return jsonify({"status": "ok", "processed_count": len(pages_to_process)}), 200

    except Exception as e:
        print(f"An error occurred in the watcher: {e}")
        return jsonify({"error": str(e)}), 500