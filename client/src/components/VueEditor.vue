<template>
  <article>
    <div :id="id" ref="quillContainer" v-on:keyup="handleKeyUp"></div>
  </article>
</template>

<script>
/* eslint-disable */
// Heavily based on https://github.com/sunkint/vue3-editor/blob/master/src/components/VueEditor.vue
import Quill from "quill";
import { defineComponent } from "vue";

export default defineComponent({
  name: "VueEditor",
  emits: [
    "ready",
    "editor-change",
    "focus",
    "selection-change",
    "text-change",
    "blur",
    "input",
    "image-removed",
    "image-added",
    "update:modelValue"
  ],
  props: {
    id: {
      type: String,
      default: "quill-container"
    },
    modelValue: {
      type: String,
      default: ""
    },
    useCustomImageHandler: {
      type: Boolean,
      default: false
    }
  },
  data: () => ({
    quill: null,
    cursorPos: 0
  }),
  watch: {
    modelValue(val) {
      if (val != this.quill.root.innerHTML && !this.quill.hasFocus()) {
        this.quill.root.innerHTML = val;
      }
    }
  },
  mounted() {
    this.registerPrototypes();
    this.initializeEditor();
  },
  beforeUnmount() {
    this.quill = null;
    delete this.quill;
  },
  methods: {
    initializeEditor() {
      this.setupQuillEditor();
      this.handleInitialContent();
      this.registerEditorEventListeners();
      this.$emit("ready", this.quill);
    },
    setupQuillEditor() {
      const bindings = {
        tab: {
          key: 9,
          handler: function(range, context) {
            console.log("Handle tab at:", range, context);
          }
        }
      };
      const editorConfig = {
        modules: {
          toolbar: false,
          keyboard: {
            bindings: bindings
          }
        },
        theme: "bubble"
      };
      this.quill = new Quill(this.$refs.quillContainer, editorConfig);
    },
    registerPrototypes() {
      Quill.prototype.getHTML = function() {
        return this.container.querySelector(".ql-editor").innerHTML;
      };
      Quill.prototype.getWordCount = function() {
        return this.container.querySelector(".ql-editor").innerText.length;
      };
    },
    registerEditorEventListeners() {
      this.quill.on("text-change", this.handleTextChange);
      this.quill.on("selection-change", this.handleSelectionChange);
      this.listenForEditorEvent("editor-change");
      this.listenForEditorEvent("text-change");
      this.listenForEditorEvent("selection-change");
    },
    listenForEditorEvent(type) {
      this.quill.on(type, (...args) => {
        this.$emit(type, ...args);
      });
    },
    handleInitialContent() {
      if (this.modelValue) this.quill.root.innerHTML = this.modelValue; // Set initial editor content
    },
    handleSelectionChange(range, oldRange, source) {
      if (!range && oldRange) this.$emit("blur", this.quill);
      else if (range && !oldRange) this.$emit("focus", this.quill);
    },
    setCursorPos() {
      const focused = this.quill.getSelection();
      if (focused) {
        this.cursorPos = focused.index;
      } else {
        this.quill.setSelection(this.quill.getLength(), 0);
        console.log("setCursorPos()", this.quill.getLength());
        this.cursorPos = this.quill.getLength();
      }
    },
    getCursorPos() {
      return this.cursorPos;
    },
    handleKeyUp(event) {
      this.quill.hasFocus() &&
        // to execute after the handler event.
        setTimeout(() => {
          this.setCursorPos(),
            console.log("KeyUP this.cursorPos", this.cursorPos),
            // Works without -1??
            this.quill.removeFormat(this.cursorPos - 1, 1, "silent");
        }, 1);
    },
    handleTextChange(delta, oldContents, source) {
      console.log("handleTextChange", this.quill.getSelection());
      let editorContent =
        this.quill.getHTML() === "<p><br></p>" ? "" : this.quill.getHTML();
      this.$emit("update:modelValue", editorContent);
    }
    // if (this.useCustomImageHandler) {
    //   this.handleImageRemoved(delta, oldContents);
    // }
    // }
    // handleImageRemoved(delta, oldContents) {
    //   const currrentContents = this.quill.getContents();
    //   const deletedContents = currrentContents.diff(oldContents);
    //   const operations = deletedContents.ops;
    //   operations.map(operation => {
    //     // eslint-disable-next-line no-prototype-builtins
    //     if (operation.insert && operation.insert.hasOwnProperty("image")) {
    //       const { image } = operation.insert;
    //       this.$emit("image-removed", image);
    //     }
    //   });
    // },
    // customImageHandler() {
    //   this.$refs.fileInput.click();
    // },
    // emitImageInfo($event) {
    //   const resetUploader = function() {
    //     const uploader = document.getElementById("file-upload");
    //     uploader.value = "";
    //   };
    //   let file = $event.target.files[0];
    //   let Editor = this.quill;
    //   let range = Editor.getSelection();
    //   let cursorLocation = range.index;
    //   this.$emit("image-added", file, Editor, cursorLocation, resetUploader);
    // }
  }
});
</script>

<style src="quill/dist/quill.bubble.css"></style>
