# Template repository for Visualization

Starter Kit for VIS &amp; ML projects

## Steps
1.  (a) **AUTOMATIC** run `./setup_new.sh <MyProjectname>` 
    
    OR (b)  **MANUALLY**

Change the PROJECTNAME (and, if needed, author/description), in the following files:
- environment.yml
- environment-dev.yml
- client/package.json
- setup.py
- client/backend/index.html

2. Select a new LICENSE (replace existing file)

3. Get client dependencies
`cd client`
`npm install --save-dev`

4. Check that client compiles:
`npm run build`

5. Setup your python environment (provided is `conda`)

`conda env create -f environment.yml`

(optional) To make your code accessible from anywhere inside this envionment, run

`pip install -e .`

6. Modify python `server/server.py` file for desired routes and the `server/api.py` file for expected types

## Running
### Backend
To start the server for development, run:

`uvicorn backend.server:app --reload`

This will auto reload the server whenever you make changes. You can deploy in a single process with:

`uvicorn backend.server:app`

Or to distribute across multiple workers, using gunicorn:

`gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.server:app`

where `4` is the number of workers desired.

### Frontend
Run `npm run watch` to watch for changes in the typescript files. 

When it is time for production, run `npm run build`

## Testing
You can run the test suite with `pytest tests`.

It is recommended that all tests for what the backend provides to the frontend be defined in `tests/test_api.py`.

Fixtures and functionality for the testing suite are a learning process.

## Notes
- You can check that the server routes work by going to `<localhost>:<port>/docs` and entering example values
- We will frequently want to incorporate someone else's code in the backend. For many researchers, their code is shared as several individual files rather than neatly packaged as a pip package. To this end, we will treat our `server` package, inside of which goes all the endpoints and the typings for the payloads and responses, as a standalone package that can be treated as standalone. The surrounding code should never import something from `server.main`, only vice versa.

### TODO
- Separate `tests/test_api` into several files called `tests/api/test_ROUTE.py`. Try to do this without recreating the `TestClient` and redefining test helper functions like `make_url` for get requests