# [FairyTailor](http://fairytailor.org/): Multimodal Generative Framework for Storytelling

### Human-in-the-loop visual story co-creation. 

Users can create a cohesive children's story by weaving generated texts and retrieved images with their input. 
With co-creation, writers contribute their creative thinking, while generative models contribute to their constant workflow. 
FairyTailor adds another modality and modifies the text generation process to help producing a coherent and creative story. 

![Architecture](framework.png)
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


After installing the environment run:
```
python -m spacy download en_core_web_sm
```
In python terminal:
```
nltk.download('wordnet')
nltk.download('sentiwordnet')
nltk.download('averaged_perceptron_tagger')
```

To run the server during development:
```
uvicorn backend.server:app --reload
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
