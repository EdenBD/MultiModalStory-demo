from functools import lru_cache
import argparse
from typing import *
import numpy as np

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import server.api as api
import path_fixes as pf

# BROKEN IMPORT
from story_generator.pipeline import Pipeline

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--port", default=8000, type=int,
                    help="Port to run the app. ")

app = FastAPI()

# Since the frontend runs on a different origin than the backend, this allows their communication.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Story:
    """
    Generated MultiModal story representation.
    """

    def __init__(self, texts, images):
        self.texts = texts
        self.images = images


@lru_cache
def getGenerator():
    """
    Function will run once thanks to cache.
    Generate an instance of the framework that generates one story.
    """
    return Pipeline(top=1)


# Main routes
@app.get("/")
def index():
    """For local development, serve the index.html in the dist folder

    NOTE: Not needed for vue cli
    """
    return RedirectResponse(url="client/index.html")


# the `file_path:path` says to accept any path as a string here. Otherwise, `file_paths` containing `/` will not be served properly
@app.get("/client/{file_path:path}")
def send_static_client(file_path: str):
    """ Serves (makes accessible) all files from ./client/ to ``/client/{path}``. Used primarily for development. NGINX handles production.

    NOTE: Not needed for Vue CLI

    Args:
        path: Name of file in the client directory
    """
    f = str(pf.DIST / file_path)
    print("Finding file: ", f)
    return FileResponse(f)

# ======================================================================
## MAIN API ##
# ======================================================================


@app.get("/api/docs")
async def docs():
    return RedirectResponse(url="/docs")


# POST to send/ create Object data, response_model converts output data to its type declaration.


@app.post("/api/post-autocomplete-img", response_model=List[str])
async def retreive_image(payload: api.ImagePayload):
    # Returns new image id strs.
    payload = api.ImagePayload(**payload)
    current_imgs = [] if payload.current is None else payload.current
    storyGenerator = getGenerator()
    return storyGenerator.retrieve_images(payload.extract, num_images=3, current_images_ids=current_imgs)


@app.post("/api/post-autocomplete-text", response_model=List[str])
async def autocomplete_text(payload: api.TextPayload):
    # Coerce into correct type. Not needed if no test written for this endpoint
    payload = api.TextPayload(**payload)
    storyGenerator = getGenerator()
    # If extracts are too long, truncation will be taken care of by the tokenizer.
    return storyGenerator.autocomplete_text(payload.extracts, max_length=30, num_return_sequences=3, re_ranking=0)


if __name__ == "__main__":
    # This file is not run as __main__ in the uvicorn environment
    args, _ = parser.parse_known_args()
    uvicorn.run("server:app", host='127.0.0.1', port=args.port)
