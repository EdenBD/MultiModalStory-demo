<template>
  <div>
    <!-- HEADER + OPTION BAR -->
    <header class="sticky">
      <div class="inner-heading">
        <div class="header-el">
          <img class="logo" src="elephant.png" />
        </div>
        <div class="header-el">
          <h1>Graphic Story Generator</h1>
          <!-- Tooltip with this info: -->
          <!-- The
          <a href="https://github.com/EdenBD/multimodal-storytelling-gan">framework</a>
          uses a guided fine-tuned
          <a href="https://huggingface.co/gpt2">GPT-2</a> text generations and
          <a href="https://github.com/unsplash/datasets">Unsplash</a> Image
          Retreival.-->
          <a
            class="info-icon"
            target="_blank"
            href="https://github.com/EdenBD/multimodal-storytelling-gan"
          >
            <i class="fa fa-info-circle" style="color: #6d6d6d"></i>
          </a>
          <div class="options">
            <div class="options-el">
              <a>
                <i class="fa fa-refresh" aria-hidden="true"></i> Generate story
                from title
              </a>
            </div>
            <div class="options-el">
              <a>
                <i class="fa fa-magic" aria-hidden="true"></i> Autocomplete
              </a>
              or
              <code>tab</code>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- DESCRIPTION -->
    <div class="description">
      <details open>
        <summary></summary>
        <div class="desciption-txt">
          <b>Step 1:</b> Change title and Generate a Story.
          <br />
          <b>Step 2:</b> continue writing and autocomplete text and images.
          <br />
          <b>Step 3:</b> Give feedback and submit your story.
        </div>
      </details>
    </div>

    <!-- MAIN EDITOR -->

    <div>
      <Editor class="editor"></Editor>
      <!-- TODO(ADD onClick Change story)-->
      <!-- TODO(ADD text autocompletion _sample_sequence onClick + keyboard) -->
      <!-- TODO(ADD image retrieval generate_images(texts_to_consider=1, one_image_retrival=True) onClick + keyboard) -->
      <!-- TODO(FORM submission database + free text form submission security issues) -->
      <!-- TODO(Loading symbol, progresss according to total time? Completed steps?) -->
      <RatingForm></RatingForm>
    </div>
  </div>
</template>

<script>
import Editor from "./components/Editor.vue";
import RatingForm from "./components/RatingForm.vue";

export default {
  name: "App",
  components: {
    Editor,
    RatingForm
  }
};
</script>

<style lang="scss">
@import "./css/palette.scss";
@import "./fonts/plex_sans.css";
@import "./css/base.scss";

/* // Add additional custom css in either the files above or here */

body {
  background-color: #eee;
  font-family: "IBM Plex Sans", sans-serif;
  font-weight: 400;
  margin: 5em;
  margin-top: 12em;
  font-size: larger;
}

.name-option {
  margin: 2px 0.3rem;
  border: solid 2px brown;
  border-radius: 2px;
}
</style>
