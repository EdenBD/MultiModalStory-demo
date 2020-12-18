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
          <a
            class="info-icon"
            target="_blank"
            href="https://github.com/EdenBD/multimodal-storytelling-gan"
            data-title="Uses huggingface, fine-tuned GPT-2 model & Unsplash Images"
          >
            <i class="fa fa-info-circle" style="color: #6d6d6d"></i>
          </a>
          <div class="options">
            <div class="options-el">
              <a @click.prevent="shuffleStory">
                <i class="fa fa-random" aria-hidden="true"></i> Shuffle Story
              </a>
            </div>
            <div class="options-el">
              <span>
                <i class="fa fa-magic" aria-hidden="true"></i>
                <code>tab</code> for
                <strong>Autocomplete</strong>
                <span class="timing">(10 sec)</span>
              </span>
            </div>
            <div class="options-el">
              <span>
                <i class="fa fa-level-up" aria-hidden="true"></i>
                <code>alt</code> or
                <code>option</code> for
                <strong>High-Quality Autocomplete</strong>
                <span class="timing">(20 sec)</span>
              </span>
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
          <b>Step 1:</b> Choose a preset or start your own story.
          <br />
          <b>Step 2:</b> Autocomplete text and images.
          <br />
          <b>Step 3:</b> Give feedback and submit your story.
        </div>
      </details>
    </div>

    <!-- MAIN EDITOR -->

    <div>
      <Editor class="editor" ref="childEditor"></Editor>
    </div>
    <Footer></Footer>
  </div>
</template>

<script>
import Editor from "./components/Editor.vue";
import Footer from "./components/Footer.vue";

const NUM_PRESET_STORIES = 5;

export default {
  name: "App",
  props: {
    routeStoryID: {
      type: String,
      // Starts with default story.
      default: "1"
    }
  },
  data: function() {
    return {
      storyID: this.routeStoryID
    };
  },
  components: {
    Editor,
    Footer
  },
  mounted: function() {
    this.$nextTick(function() {
      // Runs after all children have been rendered as well.
      this.$refs.childEditor.focus();
    });
  },
  methods: {
    shuffleStory: function() {
      // User called shuffle story
      if (this.storyID.length === 1) {
        if (Number(this.storyID) <= NUM_PRESET_STORIES) {
          this.storyID = (Number(this.storyID) + 1).toString();
        } else {
          this.storyID = "1";
        }
      }
      this.$refs.childEditor.shuffleStory(this.storyID);
    }
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
  // top | right | bottom | left
  margin: 12em 5em 0 5em;
  font-size: larger;
  min-height: 100%;
}

.name-option {
  margin: 2px 0.3rem;
  border: solid 2px brown;
  border-radius: 2px;
}
</style>
