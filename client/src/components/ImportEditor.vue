<template>
  <article class="editor">
    <VueEditor
      ref="vEditor"
      v-model="content"
      v-bind:editorToolbar="editorToolbar"
      @text-change="handleTextChange"
    ></VueEditor>
  </article>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { VueEditor, Quill } from "vue3-editor";

export default defineComponent({
  name: "Editor",
  components: {
    VueEditor
  },
  data() {
    return {
      content: `<h2 class="editable story-title" id="story-title"><strong><s>The Mighty Dragon</s></strong></h2><p></p> 
          <p><s>This creature, the Mighty Dragon, lived hundreds of years, rising in the clouds above the world and his great body slowly sinking
              beneath </s>NOT GENERATED
              <s> the earth.His power was greater than all the dragons on Mount Fuji, as his body held more power
              than all the dragons in the world. </s>
          </p>
          <img class="story-img" src="unsplash25k/sketch_images/pWzcj7wnC-c.jpg" id="story-img0" />
          <p>
            <s> So huge were his wings that he could fly over lands and water
            with the ease of a bird. It would seem that he was invincible to the Japanese, so all Japan was awed
            by the sight of the Mighty Dragon on the mountains of Fuji, only he could never make himself
            understood as a name.</s> 
          </p>
          <img class="story-img" src="unsplash25k/sketch_images/e9QFb4VVu8M.jpg" id="story-img1" />
          <p>CONTINUE STORY HERE/ THE END.</p>`,
      editorToolbar: [
        [{ header: "2" }],
        [{ size: ["small", false, "large", "huge"] }],
        ["bold", "italic", "underline"]
      ]
    };
  },

  methods: {
    handleTextChange(obj) {
      console.log("TCL: handleTextChange -> obj", obj);
    },
    setUserContent(obj) {
      console.log("USER CONTENT", obj);
    }
  }
});
</script>

// <style lang="scss">
// #app .quilWrapper .ql-toolbar .ql-snow {
//   color: red;
// }
//
</style>
