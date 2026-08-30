import os
import re
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.concurrency import run_in_threadpool

# --- Configuration ---
# Since you're dropping Docker, change this to a native host path
FILE_PATH = '/etc/caddy/domains.json' 

ALLOWED_PATTERNS = []

# Configure local logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_domains():
    """Reads the JSON file and compiles strings into Python case-insensitive Regex objects."""
    global ALLOWED_PATTERNS
    try:
        if not os.path.exists(FILE_PATH):
            logging.error(f"Configuration file missing at: {FILE_PATH}")
            return
            
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            pattern_strings = json.load(f)
            
        # Re-compile patterns dynamically into memory (case-insensitive flag)
        ALLOWED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in pattern_strings]
        logging.info(f"Successfully compiled {len(ALLOWED_PATTERNS)} regex rules into memory.")
    except Exception as e:
        logging.error(f"Error compiling domains.json: {str(e)}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles initialization and sets up non-blocking background file watching."""
    load_domains()
    
    # Simple, performant host-level file watching using standard library polling
    import asyncio
    async def file_watcher():
        last_mtime = os.path.getmtime(FILE_PATH) if os.path.exists(FILE_PATH) else 0
        while True:
            await asyncio.sleep(5)  # Poll every 5 seconds
            if os.path.exists(FILE_PATH):
                current_mtime = os.path.getmtime(FILE_PATH)
                if current_mtime != last_mtime:
                    last_mtime = current_mtime
                    logging.info("domains.json changed on disk! Re-compiling rules...")
                    # Offload blocking file I/O to Python's internal threadpool
                    await run_in_threadpool(load_domains)

    watcher_task = asyncio.create_task(file_watcher())
    yield
    watcher_task.cancel()

# Initialize FastAPI with the lifespan event listener
app = FastAPI(lifespan=lifespan)

@app.get("/allowed-domains")
async def check_allowed_domain(domain: str = Query(..., min_length=1)):
    clean_domain = domain.strip()
    
    # Evaluate against compiled regex patterns in memory
    is_matched = any(pattern.search(clean_domain) for pattern in ALLOWED_PATTERNS)
    
    if is_matched:
        return Response(status_code=200)
    
    raise HTTPException(status_code=404, detail="Domain not allowed for automated TLS.")
