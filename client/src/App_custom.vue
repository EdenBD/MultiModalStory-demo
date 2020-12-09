<template>
  <div>
    <!-- HEADER + OPTION BAR -->
    <header class="sticky">
      <div class="inner-heading">
        <div class="header-el">
          <img class="logo" src="img/elephant.png" />
        </div>
        <div class="header-el">
          <h1>Graphic Story Generator</h1>
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
                <i class="fa fa-magic" aria-hidden="true"></i> Autocomplete Text
              </a>
              or
              <code>tab</code>
            </div>
            <div class="options-el">
              <a>
                <i class="fa fa-picture-o" aria-hidden="true"></i> Retrieve
                Image
              </a>
              or
              <code>shift</code>
            </div>
          </div>
        </div>
      </div>
      <div class="seperator"></div>
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
          <br />The
          <a href="https://github.com/EdenBD/multimodal-storytelling-gan">framework</a>
          uses a guided fine-tuned
          <a href="https://huggingface.co/gpt2">GPT-2</a> text generations and
          <a href="https://github.com/unsplash/datasets">Unsplash</a> Image
          Retreival.
        </div>
      </details>
    </div>

    <!-- MAIN EDITOR -->

    <div>
      <Generated
        class="editor"
        extract="This creature, the Mighty Dragon,lived hundreds of years, rising in the clouds above the world and his great body slowly sinking beneath the earth. His power was greater than all the dragons on Mount Fuji, as his body held more power than all the dragons in the world."
      ></Generated>
      <EditableP></EditableP>
      <!-- TODO(ADD onClick Change story)-->
      <!-- TODO(ADD text autocompletion _sample_sequence onClick + keyboard) -->
      <!-- TODO(ADD image retrieval generate_images(texts_to_consider=1, one_image_retrival=True) onClick + keyboard) -->
      <!-- TODO(FORM submission database + free text form submission security issues) -->
      <!-- TODO(Loading symbol, progresss according to total time? Completed steps?) -->
      <!-- TODO(BEN - Q | MAURO - Q) -->
      <RatingForm></RatingForm>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";
import { API } from "./ts/api/mainApi";
import RatingForm from "./components/RatingForm.vue";
import Generated from "./components/Generated.vue";
import EditableP from "./components/EditableP.vue";

export default defineComponent({
  name: "App",
  components: {
    Generated,
    EditableP,
    RatingForm
  },
  setup() {
    const api = new API();
  }
});
</script>

<style lang="scss">
@import "./css/palette.scss";
@import "./fonts/plex_sans.css";
@import "./css/base.scss";

// Add additional custom css in either the files above or here

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


