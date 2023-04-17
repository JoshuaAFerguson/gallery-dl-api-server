from flask import Flask, request
from flask_restful import Api, Resource
from urllib.parse import urlparse
import sqlite3
import uuid
import subprocess
import threading
import time
import json
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
api = Api(app)

# Load configuration from JSON file


def load_config():
    with open('config.json') as config_file:
        return json.load(config_file)


config = load_config()

# Function to download a gallery using gallery-dl


def download_gallery(item_id, url):
    try:
        # Use gallery-dl to download the gallery/album
        subprocess.run(['gallery-dl', url], check=True)

        # Update the status to 'completed'
        with sqlite3.connect('gallery_dl_queue.db') as conn:
            c = conn.cursor()
            c.execute(
                "UPDATE queue SET status='completed' WHERE id=?", (item_id,))
            conn.commit()
    except subprocess.CalledProcessError as e:
        # Update the status to 'error'
        with sqlite3.connect('gallery_dl_queue.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE queue SET status='error' WHERE id=?", (item_id,))
            conn.commit()

# Function to process the queue


def process_queue():
    # Create a thread pool for parallel downloads
    with ThreadPoolExecutor(max_workers=config['parallel_downloads']) as executor:
        while True:
            try:
                # Connect to the database
                with sqlite3.connect('gallery_dl_queue.db') as conn:
                    c = conn.cursor()

                    # Find all items with status 'queued'
                    c.execute("SELECT id, url FROM queue WHERE status='queued'")
                    queued_items = c.fetchall()

                    # Submit download tasks to the thread pool
                    for item in queued_items:
                        item_id, url = item
                        # Update the status to 'downloading'
                        c.execute(
                            "UPDATE queue SET status='downloading' WHERE id=?", (item_id,))
                        conn.commit()

                        # Submit the download task to the thread pool
                        executor.submit(download_gallery, item_id, url)

            except Exception as e:
                print(f"Error processing queue: {e}")

            # Sleep for a while before checking the queue again
            time.sleep(5)


# Start the background thread to process the queue
threading.Thread(target=process_queue, daemon=True).start()

# Create an SQLite database and the queue table if they do not exist


def create_db_and_table():
    conn = sqlite3.connect('gallery_dl_queue.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS queue (
            id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Initialize the database and table
create_db_and_table()

# Function to download a gallery using gallery-dl


def download_gallery(item_id, url):
    try:
        # Use gallery-dl to download the gallery/album
        subprocess.run(['gallery-dl', url], check=True)

        # Update the status to 'completed'
        with sqlite3.connect('gallery_dl_queue.db') as conn:
            c = conn.cursor()
            c.execute(
                "UPDATE queue SET status='completed' WHERE id=?", (item_id,))
            conn.commit()
    except subprocess.CalledProcessError as e:
        # Update the status to 'error'
        with sqlite3.connect('gallery_dl_queue.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE queue SET status='error' WHERE id=?", (item_id,))
            conn.commit()

# Function to process the queue


def process_queue():
    # Create a thread pool for parallel downloads
    with ThreadPoolExecutor(max_workers=config['parallel_downloads']) as executor:
        while True:
            try:
                # Connect to the database
                with sqlite3.connect('gallery_dl_queue.db') as conn:
                    c = conn.cursor()

                    # Find all items with status 'queued'
                    c.execute("SELECT id, url FROM queue WHERE status='queued'")
                    queued_items = c.fetchall()

                    # Submit download tasks to the thread pool
                    for item in queued_items:
                        item_id, url = item
                        # Update the status to 'downloading'
                        c.execute(
                            "UPDATE queue SET status='downloading' WHERE id=?", (item_id,))
                        conn.commit()

                        # Submit the download task to the thread pool
                        executor.submit(download_gallery, item_id, url)

            except Exception as e:
                print(f"Error processing queue: {e}")

            # Sleep for a while before checking the queue again
            time.sleep(5)


# Start the background thread to process the queue
threading.Thread(target=process_queue, daemon=True).start()


class GalleryDownload(Resource):
    def post(self):
        try:
            # Parse the URL from the request data
            data = request.get_json()
            url = data.get('url')

            # Validate the URL
            if not url or not urlparse(url).scheme:
                return {'message': 'Invalid or missing URL'}, 400

            # Generate a unique ID for the queued item
            item_id = str(uuid.uuid4())

            # Insert the item into the queue with the status 'queued'
            conn = sqlite3.connect('gallery_dl_queue.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO queue (id, url, status) VALUES (?, ?, ?)
            ''', (item_id, url, 'queued'))
            conn.commit()
            conn.close()

            # Return the item ID and status to the user
            return {'id': item_id, 'url': url, 'status': 'queued'}, 200
        except Exception as e:
            return {'message': f'An error occurred: {e}'}, 500


api.add_resource(GalleryDownload, '/download')


class ResetFailedItems(Resource):
    def post(self):
        try:
            # Connect to the database
            conn = sqlite3.connect('gallery_dl_queue.db')
            c = conn.cursor()

            # Update the status of all items with status 'error' to 'queued'
            c.execute("UPDATE queue SET status='queued' WHERE status='error'")
            conn.commit()

            # Get the count of updated items
            updated_count = c.rowcount

            # Close the connection to the database
            conn.close()

            # Return the count of updated items to the user
            return {'message': f'Reset {updated_count} failed items to queued'}, 200
        except Exception as e:
            return {'message': f'An error occurred: {e}'}, 500


# Add the new endpoint to the API
api.add_resource(ResetFailedItems, '/reset_failed')


class DownloadStats(Resource):
    def get(self):
        try:
            # Connect to the database
            conn = sqlite3.connect('gallery_dl_queue.db')
            c = conn.cursor()

            # Get the count of queued items
            c.execute("SELECT COUNT(*) FROM queue WHERE status='queued'")
            queued_count = c.fetchone()[0]

            # Get the count of completed items
            c.execute("SELECT COUNT(*) FROM queue WHERE status='completed'")
            completed_count = c.fetchone()[0]

            # Get the count of failed items
            c.execute("SELECT COUNT(*) FROM queue WHERE status='error'")
            failed_count = c.fetchone()[0]

            # Close the connection to the database
            conn.close()

            # Return the counts to the user
            return {
                'queued_count': queued_count,
                'completed_count': completed_count,
                'failed_count': failed_count
            }, 200
        except Exception as e:
            return {'message': f'An error occurred: {e}'}, 500


# Add the new endpoint to the API
api.add_resource(DownloadStats, '/stats')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
