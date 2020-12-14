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
from pipeline import Pipeline

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


@app.get("/api/get-a-story")
async def generate_story(title: str):
    # Update prompt according to title
    storyGenerator = getGenerator()
    storyGenerator.update_prompt(title)
    storyGenerator.clear_prev_story()
    # Generate story of ONE top story
    # texts: [extract1, extract2] | images: [base64_JPEG1, base64_JPEG2]
    texts, images = storyGenerator.generate_graphic_story()
    return Story(texts, images)


@app.get("/api/get-image")
async def retreive_image(extract: str, img_ids=list):
    # Returns new image id strs.
    storyGenerator = getGenerator()
    return storyGenerator.retrieve_images(extract, num_images=3, current_images_ids=img_ids)


@app.get("/api/get-text")
async def generate_text(extracts: str):
    # Return text autocomplete.
    storyGenerator = getGenerator()
    return storyGenerator.autocomplete_text(extracts, max_length=20, num_return_sequences=3)


# @app.get("/api/update-images")
# async def update_used_images(img_id: str, delete: bool):
#     # Update current used img ids
#     storyGenerator = getGenerator()
#     return storyGenerator.update_current_story_images(img_id, delete)


# @app.get("/api/update-extracts")
# async def update_used_extracts(extract: str):
#     # Update current used img ids
#     storyGenerator = getGenerator()
#     return storyGenerator.update_extracts(extract)


if __name__ == "__main__":
    # This file is not run as __main__ in the uvicorn environment
    args, _ = parser.parse_known_args()
    uvicorn.run("server:app", host='127.0.0.1', port=args.port)
