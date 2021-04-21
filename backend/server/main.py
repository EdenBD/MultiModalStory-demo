from functools import lru_cache
import argparse
from typing import *
import numpy as np
# For form submission
import json
import os
import uuid

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import uvicorn
import server.api as api
import path_fixes as pf

from story_generator.pipeline import Pipeline

OUTPUT_PATH = os.path.join(
    os.getcwd(), 'backend/outputs/')

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


def _in_bounds(value, min_bound, max_bound):
    return value >= min_bound and value <= max_bound


def _verify_form(form_payload):
    MAX_STORY_LENGTH, MAX_COMMENTS_LENGTH, MAX_RATING = 30000, 150, 5
    return (_in_bounds(form_payload.coherence, 0, MAX_RATING) and _in_bounds(form_payload.clarity, 0, MAX_RATING)
            and _in_bounds(form_payload.creativity, 0, MAX_RATING) and _in_bounds(len(form_payload.freeForm), 0, MAX_COMMENTS_LENGTH)
            and _in_bounds(len(form_payload.html), 0, MAX_STORY_LENGTH))


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
    """ Serves (makes accessible) all files from ``/client/dist/{path}``. Used primarily for development. NGINX handles production.

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


@app.get("/api/story", response_model=str)
async def get_story(storyid: str):
    """
    Fetch a story HTML string if exists, otherwise returns empty string. 
    """
    file_path = os.path.join(OUTPUT_PATH, f'{storyid}.txt')
    if os.path.exists(file_path):
        try:
            with open(file_path) as infile:
                data = json.load(infile)
        except Exception as e:
            print(type(e), " Exception occurred")
            print("Exception Args:", e.args)
        else:
            return data['html']
    print("Story not found")
    return ""


# POST to send/ create Object data, response_model converts output data to its type declaration.


@app.post("/api/post-autocomplete-img", response_model=List[str])
async def retreive_image(payload: api.ImagePayload):
    # Returns new image id strs.
    payload = api.ImagePayload(**payload)
    current_imgs = [] if payload.current is None else payload.current
    storyGenerator = getGenerator()
    # Extract is the last "numSenteces" sentences defined in Editor.vue
    return storyGenerator.retrieve_images(payload.extract, num_images=3, current_images_ids=current_imgs)


@app.post("/api/post-autocomplete-text", response_model=List[str])
async def autocomplete_text(payload: api.TextPayload):
    # Coerce into correct type. Not needed if no test written for this endpoint
    payload = api.TextPayload(**payload)
    storyGenerator = getGenerator()
    # If extracts are too long, truncation will be taken care of by the tokenizer.
    re_ranking = 10 if payload.quality else 0
    # Might return less than num_return_sequences if some are empty/ just \s.
    # Returned texts are trimmed/ with one space at the beginning.
    return storyGenerator.autocomplete_text(payload.extracts, max_length=25, num_return_sequences=3, re_ranking=re_ranking)


@app.post("/api/post-form-submission", response_model=str)
async def submit_form(payload: api.FormPayload):
    # Coerce into correct type. Not needed if no test written for this endpoint
    payload = api.FormPayload(**payload)
    if _verify_form(payload):
        try:
            # Generate a unique filename, based on the payload to avoid generating two URLs for the same story + feedback.
            story_and_feedback = payload.html + \
                str(payload.creativity) + str(payload.coherence) + \
                str(payload.clarity) + payload.freeForm
            filename = uuid.uuid5(uuid.NAMESPACE_X500, story_and_feedback).hex
            file_path = os.path.join(OUTPUT_PATH, f'{filename}.txt')
            # Write new file.
            with open(file_path, 'w') as outfile:
                json.dump(dict(payload), outfile, sort_keys=True, indent=4,
                          ensure_ascii=False)
        except Exception as e:
            print(type(e), " Exception occurred")
            print("Excetopn Args:", e.args)
        # If there are no exceptions
        else:
            return filename
    return ""

if __name__ == "__main__":
    # This file is not run as __main__ in the uvicorn environment
    args, _ = parser.parse_known_args()
    uvicorn.run("server:app", host='127.0.0.1', port=args.port)
