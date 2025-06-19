from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import psycopg2

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Set up your PostgreSQL connection
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="your_db",
        user="your_user",
        password="your_password"
    )

@app.get("/", response_class=HTMLResponse)
def read_results(request: Request):
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT s.original_channel_code, COUNT(*) AS count
        FROM recording r
        LEFT JOIN source s ON s.source_id = r.source_id
        LEFT JOIN channel c ON c.channel_id = s.source_id
        WHERE s.original_channel_code IN (
            'BBCArabicTV','BBCNews','BBCPersianTV','GBR75BBC5LiveBBC','GBR38BBC5LiveSportsExtra',
            'GBT32Parliament','GBT321BBCWorldNews','BBCWSEastAfrica','GBR18BBCRadio4',
            'GBR186BBCSportsExtra2','GBR187BBCSportsExtra3','GBT123RedButton'
        )
        AND to_timestamp(r.date_created) >= '2025-05-01'::timestamp
        AND to_timestamp(r.date_created) < '2025-06-01'::timestamp
        GROUP BY s.original_channel_code
        ORDER BY count DESC;
    """

    cur.execute(query)
    results = cur.fetchall()
    cur.close()
    conn.close()

    return templates.TemplateResponse("results.html", {"request": request, "results": results})
