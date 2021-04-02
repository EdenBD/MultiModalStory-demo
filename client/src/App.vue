<template>
  <v-app id="vapp">
    <div>
      <div class="small-screen">
        We're sorry, but we do not currently support smaller screens.
      </div>
      <div class="big-screen">
        <Editor></Editor>
        <Footer></Footer>
      </div>
    </div>
  </v-app>
</template>

<script>
import Editor from "./components/Editor.vue";
import Footer from "./components/Footer.vue";

export default {
  name: "App",
  components: {
    Editor,
    Footer,
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
