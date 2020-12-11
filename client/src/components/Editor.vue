<template>
  <article>
    <template>
      <editor-content :editor="editor" />
    </template>
  </article>
</template>

<script>
// Import the basic building blocks
import { Editor, EditorContent } from "tiptap";
import Doc from "../nodes/Doc";
import Title from "../nodes/Title";
import { Placeholder, Strike } from "tiptap-extensions";

export default {
  name: "Editor",
  components: {
    EditorContent
  },
  data() {
    return {
      // Default content. Editor is passed to `EditorContent` component as a `prop`.
      editor: new Editor({
        autofocus: true,
        disableInputRules: ["strike"],
        content:
          "<h2>The Mighty Dragon</h2><p>I was blind, <s>That's generated.</s></p>",
        extensions: [
          new Doc(),
          new Title(),
          new Strike(),
          new Placeholder({
            showOnlyCurrent: false,
            emptyNodeText: node => {
              if (node.type.name === "title") {
                return "Your Story Title";
              }
              return "Write something awesome...";
            }
          })
        ],
        // onUpdate: ({ getHTML }) => {
        //   // get new content on update
        //   console.log("getHTML()", getHTML());
        // },
        editorProps: {
          // Open options menu.
          handleKeyDown: (view, event) => {
            if (event.key === "Tab") {
              event.preventDefault();
              const cursorPosition = view.state.selection.anchor;
              const allText = view.dom.innerText;
              console.log("view", cursorPosition, allText);
            }
          }
          // handleTextInput: (view, from, to) => {
          //   let marked = view.state.doc.rangeHasMark(from, to, "strike");
          //   console.log("marked", marked);
          //   if (marked) {
          //     view.state.tr.removeMark(from, to, "strike");
          //   }
          //   return false;
          // }
        }
      })
    };
  },
  beforeDestroy() {
    this.editor.destroy();
  }
};

// this.editor.commands to insert images/ text.
</script>


<style lang="scss">
.editor *.is-empty:nth-child(1)::before,
.editor *.is-empty:nth-child(2)::before {
  content: attr(data-empty-text);
  float: center;
  color: #aaa;
  pointer-events: none;
  height: 0;
  font-style: italic;
}
</style>
