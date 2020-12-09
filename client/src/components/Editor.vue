<template>
  <VueEditor
    ref="vEditor"
    v-model="content"
    useCustomImageHandler
    @focus="onEditorFocus"
    @blur="onEditorBlur"
    @imageAdded="handleImageAdded"
    @image-removed="handleImageRemoved"
    @ready="setCursor"
  ></VueEditor>
</template>

<script>
// Heavily based on https://github.com/sunkint/vue3-editor/blob/master/src/App.vue

import axios from "axios";
import Quill from "quill";
import VueEditor from "./VueEditor.vue";
import { defineComponent } from "vue";

const AlignStyle = Quill.import("attributors/style/align");
Quill.register(AlignStyle, true);

const BlockEmbed = Quill.import("blots/block/embed");

/**
 * Customize image so we can add an `id` attribute
 */
class ImageBlot extends BlockEmbed {
  static create(value) {
    const node = super.create();
    node.setAttribute("src", value.url);
    node.setAttribute("id", value.id);
    return node;
  }

  static value(node) {
    return {
      url: node.getAttribute("src"),
      id: node.getAttribute("id")
    };
  }
}

ImageBlot.blotName = "image";
ImageBlot.tagName = "img";
Quill.register(ImageBlot);

export default defineComponent({
  name: "Editor",
  components: {
    VueEditor
  },
  data: () => ({
    content: `<h2>The Mighty Dragon</h2><p></p><p><s>This creature</s>, the Mighty Dragon, the dragons in the world.</p><img class="story-img" src="unsplash25k/sketch_images/pWzcj7wnC-c.jpg" id="pWzcj7wnC-c" /><p>CONTINUE STORY HERE/ THE END.</p>`
    // content: `<h2>The Mighty Dragon</h2><p></p><p class="generated" contenteditable="false">This creature, the Mighty Dragon,lived hundreds of years, rising in the clouds above the world and his great body slowly sinking beneath the earth. His power was greater than all the dragons on Mount Fuji, as his body held more power than all the dragons in the world.</p><img class="story-img" src="unsplash25k/sketch_images/pWzcj7wnC-c.jpg" id="pWzcj7wnC-c" /><p>CONTINUE STORY HERE/ THE END.</p>`
  }),

  methods: {
    setCursor(quill) {
      // set cursor at the end.
      quill.blur();
      quill.focus();
    },
    handleTextChange(obj) {
      console.log("TCL: handleTextChange -> obj", obj);
    },

    onEditorBlur(quill) {
      console.log("editor blur!", quill);
    },

    onEditorFocus(quill) {
      console.log("editor focus!", quill);
    },

    handleImageAdded(id, Editor, cursorLocation) {
      console.log("TCL: handleImageAdded id:", id);

      Editor.insertEmbed(
        cursorLocation,
        "image",
        {
          id,
          url: `unsplash25k/sketch_images/${id}.jpg`
        },
        Quill.sources.USER
      );
    },

    handleImageRemoved(image) {
      console.log("handleImageRemoved -> image", image);
    }
  }
});
</script>
