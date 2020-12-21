# MultiModalStory Demo - based on VISStarter

## Client

Uses Vue 3.0 + Typescript.

Consider converting main page into components, it'll be easier to keep track of

(development)

```
cd client
npm i
npm run serve
```

## Backend

(development)

```
uvicorn backend.server:app --reload
```

- After installing the environment run:
```
python -m spacy download en_core_web_sm
nltk.download('wordnet')
nltk.download('sentiwordnet')
```

## Large Data Management
We use a tool called [dvc](https://dvc.org/) which to version control large data files like git version controls code. 

These are stored on IBM's Cloud Object Storage, and to push or pull data files to that platform you will need a special `.dvc/config` file.

Setting up:
1. Ensure you have config file
2. `conda env update -f environment.yml` # Installs dvc

To upload:

``` bash
dvc add backend/outputs backend/story_generator/downloaded client/public/unsplash25k
git add *.dvc
dvc push
git commit "Added large files to version control"
```

To pull data:
```
dvc pull
```

# Notes
- To interactively hit backend routes, go to `localhost:8000/docs` (i.e., the server running the backend not the Vue server)
