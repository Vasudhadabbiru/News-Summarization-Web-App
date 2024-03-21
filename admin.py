import psycopg2
from scraper import scraper
from summarizer import summarizer
import time

# Connect to PostgreSQL database
DB_HOST = "localhost"
DB_NAME = "sampledb"
DB_USER = "postgres"
DB_PASS = "Vasudhap@#*?2001"
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

# Function to summarize URLs and update the database
def summarize_urls():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, url FROM editorials")
        rows = cursor.fetchall()

        for row in rows:
            editorial_id, url = row
            try:
                article_title, text = scraper(url)
                summary = summarizer(text)

            # Update the database with the summary
                cursor.execute("UPDATE editorials SET summary = %s WHERE id = %s", (summary, editorial_id))
                conn.commit()

                print(f"Summary generated and updated for URL with ID {editorial_id}")
                time.sleep(10)
            except Exception as e:
                print(f"Error processing URL with ID {editorial_id}: {e}")
                continue

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error:", error)

    finally:
        if conn is not None:
            conn.close()

# Call the function to summarize URLs and update the database
summarize_urls()
