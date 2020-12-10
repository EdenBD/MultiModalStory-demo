<template>
  <VueEditor
    ref="vEditor"
    v-model="content"
    useCustomImageHandler
    @focus="onEditorFocus"
    @blur="onEditorBlur"
    @image-removed="handleImageRemoved"
    @text-change="handleTextChange"
    @autocoomplete-trigger="autocomplete"
    @ready="setEditorFocus"
  ></VueEditor>
</template>

<script>
/* eslint-disable */
// Heavily based on https://github.com/sunkint/vue3-editor/blob/master/src/App.vue

import axios from "axios";
import Quill from "quill";
import VueEditor from "./VueEditor.vue";
import { defineComponent } from "vue";
import { API } from "../ts/api/mainApi";

const AlignStyle = Quill.import("attributors/style/align");
Quill.register(AlignStyle, true);

const BlockEmbed = Quill.import("blots/block/embed");
const Embed = Quill.import("blots/embed");
const Inline = Quill.import("blots/inline");
/**
 * Customize image so we can add an `id` attribute
 */
class ImageBlot extends BlockEmbed {
  static create(value) {
    const node = super.create();
    node.setAttribute("src", value.url);
    node.setAttribute("id", value.id);
    // node.classList.add("story-img");
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

class Generated extends Embed {
  // Overriding this method, in this particular case, is what
  // causes the Delta returned as content by Quill to have
  // the desired information.
  static create(value) {
    if (!value) return super.create(false);
    const node = super.create(value);
    // node.innerText = value;
    node.innerHTML = value;
    node.addEventListener("click", Generated.onClick);
    return node;
  }
  //Returns the value of the node itself for undo operation
  static value(node) {
    return node.innerHTML;
  }
  // Overriding required for formattable classes.
  // static formats(domNode) {
  //   if (domNode.classList.contains("generated")) {
  //     return true;
  //   } else {
  //     return super.formats(domNode);
  //   }
  // }

  // formats() {
  //   let formats = super.formats();
  //   formats["generated"] = Generated.formats(this.domNode);
  //   return formats;
  // }
}

Generated.blotName = "generated";
Generated.tagName = "generated";
Generated.className = "generated";
Generated.onClick = function() {
  console.log("generated clicked");
};
Quill.register(Generated);

export default defineComponent({
  name: "Editor",
  components: {
    VueEditor
  },
  setup() {
    const api = new API();
  },
  data: () => ({
    imagesIds: ["pWzcj7wnC-c"],
    // Manually copy imageID in content
    content: "<p>ABCD</p><p><br></p><p><br></p>"
    // content: `<h2>The Mighty Dragon</h2><p></p><p>This creature, the Mighty Dragon, the dragons in the world.</p><img class="story-img" src="unsplash25k/sketch_images/pWzcj7wnC-c.jpg" id="pWzcj7wnC-c" /><p>CONTINUE STORY HERE/ THE END.</p>`
  }),
  methods: {
    getEditor() {
      return this.$refs.vEditor.quill;
    },
    updateEditorCursor(val = null) {
      if (val !== null) {
        return (this.$refs.vEditor.cursorPos = val);
      }
      return this.$refs.vEditor.setCursorPos();
    },
    setEditorFocus() {
      // console.log("fired ready");
      // Set cursor at page load.
      this.getEditor().blur();
      this.getEditor().focus();
    },
    handleTextChange(delta) {
      // delta ofter the change
      // console.log("Editor: handleTextChange -> delta", delta);
      console.log(
        "Editor: handleTextChange getText",
        this.getEditor().getText()
      );
      // console.log("Editor: html", this.getEditor().getHTMLText());
    },

    onEditorBlur(quill) {
      console.log("editor blur!", quill);
    },

    onEditorFocus(quill) {
      console.log("editor focus!", quill);
    },

    addImage(cursorLocation, id) {
      console.log("Editor: addImage id:", id);
      // Keep track of current images.
      this.imagesIds.push(id);

      const delta = this.getEditor().insertEmbed(
        cursorLocation,
        "image",
        {
          id,
          url: `unsplash25k/sketch_images/${id}.jpg`
        },
        Quill.sources.API
      );
      console.log("IMG delta", delta);
      this.getEditor().setSelection(1 + cursorLocation);
      this.updateEditorCursor();
    },

    addGenerated(cursorLocation, generatedText) {
      // Keep track of current images.
      this.getEditor().insertText(
        cursorLocation,
        generatedText,
        Quill.sources.API
      );
      // Update cursor to after inserted text.
      this.getEditor().setSelection(cursorLocation + generatedText.length, 0);
      const newCursorPos = this.updateEditorCursor();
      // this.getEditor().insertEmbed(
      //   cursorLocation,
      //   "generated",
      //   generatedText,
      //   Quill.sources.API
      // );
      // let cursorPos = this.$refs.vEditor.setCursorPos();
      // console.log("cursorPos1", cursorPos);
      // this.getEditor().insertText(newCursorPos, " ");
      // this.getEditor().setSelection(newCursorPos + 1, 0);
      // this.updateEditorCursor();
      // console.log("cursorPos2", this.getEditor().getLength() + 1);
      // setTimeout(() => {
      //   this.getEditor().setSelection(
      //     this.getEditor().getLength() + 1,
      //     Quill.sources.SILENT
      //   );
      // });
    },

    handleImageRemoved(image) {
      // Update current image ids.
      this.imagesIds = this.imagesIds.filter(i => i !== image.id);
      console.log("handleImageRemoved -> image", image.id, this.imagesIds);
    },

    autocomplete(selectionRange) {
      // get current Text
      const cursorLocation = selectionRange.index;
      console.log("tag pos", cursorLocation);
      const cursorRange = selectionRange.length;
      const text = String(this.getEditor().getText());
      // this.addGenerated(cursorLocation, "XXX");
      this.addImage(cursorLocation, "zZzKLzKP24o");
      // Process text: For images - use the past three senteces.
      // Process text: For text trim to 500 tokens from the end.
    }
  }
});
</script>
