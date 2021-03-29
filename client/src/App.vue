<template>
  <v-app id="vapp">
    <div>
      <div class="small-screen">
        We're sorry, but we do not currently support smaller screens.
      </div>
      <div class="big-screen">
        <Editor ref="childEditor"></Editor>
        <Footer></Footer>
      </div>
    </div>
  </v-app>
</template>

<script>
import Editor from "./components/Editor.vue";
import Footer from "./components/Footer.vue";

const NUM_PRESET_STORIES = 5;

export default {
  name: "App",
  data: function () {
    return {
      storyID: this.$route.params.storyid || "1",
    };
  },
  components: {
    Editor,
    Footer,
  },
  watch: {
    $route() {
      this.storyID = this.$route.params.storyid;
    },
  },
  methods: {
    shuffleStory: function () {
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
    },
  },
};
</script>

<style lang="scss">
@import "./css/palette.scss";
@import "./fonts/plex_sans.css";
@import "./css/base.scss";

/* // Add additional custom css in either the files above or here */

body {
  background-color: #eee;
  font-family: "Source Sans Pro", Calibri, Candara, Arial, sans-serif;
  font-weight: 400;
  // top | right | bottom | left
  margin: 12em 5em 0 5em;
  min-height: 100%;
}

.name-option {
  margin: 2px 0.3rem;
  border: solid 2px brown;
  border-radius: 2px;
}
</style>
