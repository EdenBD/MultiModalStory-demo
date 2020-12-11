<template>
  <article>
    <template>
      <editor-content ref="editor" :editor="editor" />
    </template>
  </article>
</template>

<script lang="js">
// Import the basic building blocks
import { Editor, EditorContent } from "tiptap";
import Doc from "../nodes/Doc";
import Title from "../nodes/Title";
import { Placeholder, Strike, Image } from "tiptap-extensions";
import { API } from "../js/api/mainApi";

export default {
  name: "Editor",
  components: {
    EditorContent
  },
  setup() {
    const api = new API();
    console.log(api);
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
          new Image(),
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
              console.log("cursor | text", cursorPosition, allText);
            }
          },
          handleTextInput: (view, from, to, text) => {
            // Learned from similar code: https://gitmemory.com/issue/scrumpy/tiptap/490/565634509.
            // For all char keys, to distinguish generated from user text.
            const [strike] = view.state.tr.selection.$anchor.marks();
            const isStrike = strike && strike.type.name === "strike";
            // If user writes inside genrated text.
            console.log("isStrike",isStrike,"text",text,from, to)
            if (isStrike) {
              // Add a space before the inserted char
              setTimeout(()=> {view.dispatch(view.state.tr.insertText(' ', from));})
              setTimeout(()=> {view.dispatch(view.state.tr.removeMark(from, to+2, strike));})
            }
            // To maintain the normal behavior of user input.
            return false;
          }
        }
      })
    };
  },
  beforeDestroy() {
    this.editor.destroy();
  },
  methods: {
    insertImage(command, imgId = "__CmMNKO4nw") {
      if (imgId !== null) {
        const src = `unsplash25k/sketch_images/${imgId}.jpg`;
        command({ src });
      }
    }
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
