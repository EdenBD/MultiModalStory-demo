<template>
  <div>
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
            <i class="fa fa-info-circle" style="color: #6d6d6d;"></i>
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
              or <code> tab </code>
            </div>
            <div class="options-el">
              <a>
                <i class="fa fa-picture-o" aria-hidden="true"></i> Retrieve Image
              </a>
              or
              <code> shift </code>
            </div>
          </div>
        </div>
      </div>
      <div class="seperator"></div>
    </header>
    <div class="description">
      <details open>
        <summary></summary>
        <div class="desciption-txt">
          <b>Step 1:</b> Change title and Generate a Story. <br />
          <b>Step 2:</b> continue writing and autocomplete text and images. <br />
          <b>Step 3:</b> Give feedback and submit your story. <br />
          The<a href="https://github.com/EdenBD/multimodal-storytelling-gan">
            framework</a
          >
          uses a guided fine-tuned
          <a href="https://huggingface.co/gpt2">GPT-2</a> text generations and
          <a href="https://github.com/unsplash/datasets">Unsplash</a> Image
          Retreival.
        </div>
      </details>
    </div>
  
    <div>
      <article>
        <!-- TODO(ADD onClick Change story)-->
        <!-- TODO(ADD text autocompletion _sample_sequence onClick + keyboard) -->
        <!-- TODO(ADD image retrieval generate_images(texts_to_consider=1, one_image_retrival=True) onClick + keyboard) -->
        <!-- TODO(FORM submission database + free text form submission security issues) -->
        <!-- TODO(Loading symbol, progresss according to total time? Completed steps?) -->
        <!-- TODO(BEN - Q | MAURO - Q) -->
        <h2 class="editable story-title" contenteditable="true" id="story-title">
          The Mighty Dragon
        </h2>
        <div id="story-article">
          <p class="editable" contenteditable="true" id="story-p0">
            This creature, the Mighty Dragon, lived hundreds of years, rising in
            the clouds above the world and his great body slowly sinking beneath
            the earth. His power was greater than all the dragons on Mount Fuji,
            as his body held more power than all the dragons in the world.
          </p>
          <img
            class="story-img"
            src="unsplash25k/sketch_images/pWzcj7wnC-c.jpg"
            id="story-img0"
          />
          <p class="editable" contenteditable="true" id="story-p1">
            So huge were his wings that he could fly over lands and water with the
            ease of a bird. It would seem that he was invincible to the Japanese,
            so all Japan was awed by the sight of the Mighty Dragon on the
            mountains of Fuji, only he could never make himself understood as a
            name.
          </p>
          <img
            class="story-img"
            src="unsplash25k/sketch_images/e9QFb4VVu8M.jpg"
            id="story-img1"
          />
          <p class="editable" contenteditable="true">
            CONTINUE STORY HERE ...
          </p>
        </div>
      </article>
  
      <article class="ratings-card">
        <h3 class="card-title">Score Auto-Generated Story</h3>
        <form id="scores" action="#" method="post">
          <!-- CLARITY: readability, simplicity, coherence -->
          <div>
            <h4 class="card-title rating-el-title-el">Clarity</h4>
            <div class="rating-el-title-el star-rating">
              <fieldset>
                <!-- same name attributes ensures users can only choose one star -->
                <input
                  type="radio"
                  id="clarity-star5"
                  name="clarity-rating"
                  value="5"
                /><label for="clarity-star5" title="Outstanding">5 stars</label>
                <input
                  type="radio"
                  id="clarity-star4"
                  name="clarity-rating"
                  value="4"
                /><label for="clarity-star4" title="Very Good">4 stars</label>
                <input
                  type="radio"
                  id="clarity-star3"
                  name="clarity-rating"
                  value="3"
                /><label for="clarity-star3" title="Good">3 stars</label>
                <input
                  type="radio"
                  id="clarity-star2"
                  name="clarity-rating"
                  value="2"
                /><label for="clarity-star2" title="Poor">2 stars</label>
                <input
                  type="radio"
                  id="clarity-star1"
                  name="clarity-rating"
                  value="1"
                /><label for="clarity-star1" title="Very Poor">1 star</label>
              </fieldset>
            </div>
          </div>
          <!-- COHERENCY: tale like, diversity -->
          <div>
            <h4 class="card-title rating-el-title-el">Coherence</h4>
            <div class="rating-el-title-el star-rating">
              <fieldset>
                <input
                  type="radio"
                  id="coherence-star5"
                  name="coherence-rating"
                  value="5"
                /><label for="coherence-star5" title="Outstanding">5 stars</label>
                <input
                  type="radio"
                  id="coherence-star4"
                  name="coherence-rating"
                  value="4"
                /><label for="coherence-star4" title="Very Good">4 stars</label>
                <input
                  type="radio"
                  id="coherence-star3"
                  name="coherence-rating"
                  value="3"
                /><label for="coherence-star3" title="Good">3 stars</label>
                <input
                  type="radio"
                  id="coherence-star2"
                  name="coherence-rating"
                  value="2"
                /><label for="coherence-star2" title="Poor">2 stars</label>
                <input
                  type="radio"
                  id="coherence-star1"
                  name="coherence-rating"
                  value="1"
                /><label for="coherence-star1" title="Very Poor">1 star</label>
              </fieldset>
            </div>
          </div>
          <!-- CREATIVITY: tale like, diversity -->
          <div>
            <h4 class="card-title rating-el-title-el">Creativity</h4>
            <div class="rating-el-title-el star-rating">
              <fieldset>
                <input
                  type="radio"
                  id="creativity-star5"
                  name="creativity-rating"
                  value="5"
                /><label for="creativity-star5" title="Outstanding"
                  >5 stars</label
                >
                <input
                  type="radio"
                  id="creativity-star4"
                  name="creativity-rating"
                  value="4"
                /><label for="creativity-star4" title="Very Good">4 stars</label>
                <input
                  type="radio"
                  id="creativity-star3"
                  name="creativity-rating"
                  value="3"
                /><label for="creativity-star3" title="Good">3 stars</label>
                <input
                  type="radio"
                  id="creativity-star2"
                  name="creativity-rating"
                  value="2"
                /><label for="creativity-star2" title="Poor">2 stars</label>
                <input
                  type="radio"
                  id="creativity-star1"
                  name="creativity-rating"
                  value="1"
                /><label for="creativity-star1" title="Very Poor">1 star</label>
              </fieldset>
            </div>
          </div>
          <h4 class="card-title rating-el-title-el">
            Any comments, questions or suggestions?
          </h4>
          <textarea rows="3"></textarea>
          <div class="submit-bttn card-title">
            <input type="submit" value="Submit Story" />
          </div>
        </form>
      </article>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, watchEffect } from "vue";
import { API } from "./ts/api/mainApi";
import HelloWorld from "./components/HelloWorld.vue";

export default defineComponent({
  name: "App",
  components: {
    // HelloWorld
  },
  setup() {
    const msg = ref("Welcome to Vue, Eden");
    const api = new API();

    function buttonClick() {
      api.getAHi("Ben").then(r => {
        msg.value = r;
      });
    }

    return {
      msg,
      buttonClick
    };
  }
});
</script>

<style lang="scss">
@import "./css/palette.scss";
@import "./fonts/plex_sans.css";
@import "./css/base.scss";

body {
  background-color:#eee;
  font-family: 'IBM Plex Sans', sans-serif;
  font-weight: 400;
  margin: 5em;
  margin-top: 12em;
  font-size: larger;
}


// #app {
//   font-family: Avenir, Helvetica, Arial, sans-serif;
//   -webkit-font-smoothing: antialiased;
//   -moz-osx-font-smoothing: grayscale;
//   text-align: center;
//   color: #2c3e50;
//   margin-top: 60px;
// }
</style>
