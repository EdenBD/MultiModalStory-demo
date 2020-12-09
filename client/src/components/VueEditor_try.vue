<template>
  <article>
    <div :id="id" ref="quillContainer" v-on:keydown="handleKeyDown"></div>
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
      const editorConfig = {
        modules: {
          toolbar: false
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
    handleKeyDown() {
      console.log("key down");
      //   this.setCursorPos();
    },
    handleTextChange(delta, oldContents, source) {
      console.log("handleTextChange", this.quill.getSelection());
      let editorContent =
        this.quill.getHTML() === "<p><br></p>" ? "" : this.quill.getHTML();
      this.$emit("update:modelValue", editorContent);
      const isInsertInGenerated = delta.ops.some(
        A => A.attributes && !0 === A.attributes.strike
      );
      if (this.quill.hasFocus()) {
        setTimeout(() => {
          const insertOps = delta["ops"].filter(o => "insert" in o);
          const retainOps = delta["ops"].filter(o => "retain" in o);
          if (insertOps.length == 1 && retainOps.length == 1) {
            let charIndex = retainOps[0]["retain"];
            this.quill.setSelection(charIndex + 1, 0);
            // Changing format changes the tag and thrrows off indexing?
            this.quill.removeFormat(charIndex, 1, "silent");
            if (isInsertInGenerated) {
              console.log("charIndex", charIndex);
            }
          }
        }, 1);
      }
      //   CHECK IF DELTA INCLUDES INSERT
      if (this.useCustomImageHandler) {
        this.handleImageRemoved(delta, oldContents);
      }
      //   if (source === "user") {
      //     let insertEvents = delta.ops.filter(op => op.hasOwnProperty("insert"));
      //     if (insertEvents.length === 0 || this.quill.getSelection() === null)
      //       return;
      //     console.log("delta", delta);
      //     this.quill.format("strike", false);
      //     let cursorIndex = this.quill.getSelection().index;
      //     console.log("insert: cursorIndex", cursorIndex);
      //     let curFormat = this.quill.getFormat(cursorIndex, 1);
      //     if (curFormat !== null) {
      //       console.log("curFormat.strike", curFormat.strike);
      //   if (curFormat.strike) {
      //     this.quill.formatText(cursorIndex, 1, "strike", false);
      //   }
      // }
    },
    // handleEditorChange(eventName, delta, oldContents, source) {
    //   if (eventName === "text-change") {
    //     console.log("handleEditorChange");
    //     console.log("delta", delta);
    //     const insertOps = delta["ops"].filter(o => "insert" in o);
    //     if (insertOps.length == 1) {
    //       const insert = insertOps[0]["insert"];
    //       if (insert.length == 1 && this.quill.getSelection() !== null) {
    //         const charIndex =
    //           this.quill.getSelection().index - 1 >= 0
    //             ? this.quill.getSelection().index - 1
    //             : 0;
    //         const curFormat = this.quill.getFormat(charIndex, 1);
    //         if (curFormat !== null && curFormat.strike) {
    //           console.log("insert:", insert, insert.length);
    //           console.log("charIndex", charIndex);

    //           this.quill.formatText(charIndex, 1, "strike", true);
    //           this.quill.update();
    //         }
    //       }
    //     }
    //   }
    // },
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
    },
    customImageHandler() {
      this.$refs.fileInput.click();
    },
    emitImageInfo($event) {
      const resetUploader = function() {
        const uploader = document.getElementById("file-upload");
        uploader.value = "";
      };
      let file = $event.target.files[0];
      let Editor = this.quill;
      let range = Editor.getSelection();
      let cursorLocation = range.index;
      this.$emit("image-added", file, Editor, cursorLocation, resetUploader);
    }
  }
});
</script>

<style src="quill/dist/quill.bubble.css"></style>
