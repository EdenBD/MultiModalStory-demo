<template>
  <article>
    <!-- Add v-on:keyup="handleKeyUp" if works! -->
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
    "autocoomplete-trigger",
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
    // Adds content at the beggining anf keeps the child synced with Editor
    modelValue(val) {
      if (val != this.quill.root.innerHTML && !this.quill.hasFocus()) {
        console.log("modelValue val:", val);
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
        // In init to overide default tab behavior.
        tab: {
          key: 9,
          handler: (range, context) => {
            this.$emit("autocoomplete-trigger", range);
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
      Quill.prototype.getHTMLText = function() {
        return this.container.querySelector(".ql-editor").innerText;
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
        console.log(
          "setCursorPos used quill.getLength",
          this.quill.getLength()
        );
        this.cursorPos = this.quill.getLength();
      }
      return this.cursorPos;
    },
    handleKeyUp(event) {
      this.quill.hasFocus() &&
        // to execute after the handler event.
        setTimeout(() => {
          this.setCursorPos();
          console.log("KeyUP this.cursorPos", this.cursorPos);
          //   const curFormat = this.quill.getFormat(this.cursorPos - 1, 1);
          //   if (curFormat !== null && curFormat.strike) {
          //     // Works without -1??
          //     this.quill.formatText(this.cursorPos, 1, "strike", false);
          //   }
        }, 0);
    },
    handleTextChange(delta, oldContents, source) {
      let editorContent =
        this.quill.getHTML() === "<p><br></p>" ? "" : this.quill.getHTML();
      this.$emit("update:modelValue", editorContent);

      if (this.useCustomImageHandler) {
        this.handleImageRemoved(delta, oldContents);
      }

      if (this.useGeneratedTextHandler) {
        this.handleGeneratedRemoved(delta, oldContents);
      }
    },
    handleImageRemoved(delta, oldContents) {
      const currrentContents = this.quill.getContents();
      const deletedContents = currrentContents.diff(oldContents);
      const operations = deletedContents.ops;
      operations.map(operation => {
        // eslint-disable-next-line no-prototype-builtins
        if (operation.insert && operation.insert.hasOwnProperty("image")) {
          const { image } = operation.insert;
          this.$emit("image-removed", image);
        }
      });
    }
  }
});
</script>

<style src="quill/dist/quill.bubble.css"></style>
