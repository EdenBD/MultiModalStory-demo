<template>
  <div>
    <!-- HEADER + OPTION BAR -->
    <header class="sticky">
      <div class="inner-heading">
        <div class="header-el">
          <img class="logo" src="elephant.png" />
        </div>
        <div class="header-el">
          <a
            href="https://github.com/EdenBD/MultiModalStory-demo"
            target="_blank"
            data-title="Uses GPT-2 & Unsplash Images to generate text-and-images stories"
          >
            <img class="title-logo shadow" src="logo2.png" />
          </a>
          <div class="options">
            <div class="options-el clickable">
              <a @click.prevent="shuffleStory">
                <i class="fa fa-random" aria-hidden="true"></i> Shuffle Story
              </a>
            </div>
            <div class="options-el shadow clean-format">
              <a data-title="Generates up to three text completions and images">
                <i class="fa fa-magic" aria-hidden="true"></i>
                <code>tab</code> for
                <strong>Autocomplete</strong>
                <span class="timing">(2 sec)</span>
              </a>
            </div>
            <div class="options-el shadow clean-format">
              <a
                data-title="Returns top-ranked texts according to creativity, readability, coherency, and positivity measures"
              >
                <i class="fa fa-level-up" aria-hidden="true"></i>
                <code>shift</code> +
                <code>tab</code> for
                <strong>High-Quality Autocomplete</strong>
                <span class="timing">(5 sec)</span>
              </a>
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
  data: function() {
    return {
      storyID: this.$route.params.storyid || "1"
    };
  },
  components: {
    Editor,
    Footer
  },
  watch: {
    $route() {
      this.storyID = this.$route.params.storyid;
    }
  },
  methods: {
    shuffleStory: function() {
      // User called shuffle story from default story
      if (this.storyID.length === 1) {
        // Once tried all default stories, return to default storyID=1.
        this.storyID = (
          (Number(this.storyID) % NUM_PRESET_STORIES) +
          1
        ).toString();
        // User called shuffle after submitting a form
      } else {
        this.storyID = "2";
      }
      // Update the route.
      this.$router.push({ name: "story", params: { storyid: this.storyID } });
      // Update the editor content.
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
