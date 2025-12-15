from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging
import time

logger = logging.getLogger("uvicorn.access")
logger.disabled = True

def register_all_middleware(app: FastAPI):
    @app.middleware("http")
    async def custom_logger_middleware(request, call_next):
        start_time = time.time()
       
        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        formatted_process_time = f"{process_time:.2f}ms"

        status = getattr(response, "status_code", 0)
        if status >= 500:
            status_color, emoji = "\x1b[31m", "💥"
        elif status >= 400:
            status_color, emoji = "\x1b[91m", "❌"
        elif status >= 300:
            status_color, emoji = "\x1b[33m", "🔁"
        else:
            status_color, emoji = "\x1b[32m", "✅"

        method_color = "\x1b[36m"
        url_color = "\x1b[34m"
        time_color = "\x1b[35m"
        reset = "\x1b[0m"

        print(
            f"\n"
            f"{emoji} {method_color}{request.method}{reset} "
            f"{url_color}{request.url.path}{reset} -> "
            f"{status_color}{status}{reset} "
            f"completed in {time_color}{formatted_process_time}{reset} \n"
        )

        return response 
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )