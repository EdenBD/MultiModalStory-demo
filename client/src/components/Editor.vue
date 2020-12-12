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
import { Placeholder, Strike, Image,  TrailingNode } from "tiptap-extensions";
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
        // Update handleKeyDown.currentImgs in case of adding new images tags. 
        content:
          "<h2>The Mighty Dragon</h2><p>I was blind, <s>That's generated.</s></p>",
        extensions: [
          new Doc(),
          new Title(),
          new Strike(),
          new Image(),
          new TrailingNode({
            node: 'paragraph',
            notAfter: ['paragraph'],
          }),
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
        onUpdate: ({ getJSON }) => {
          // Update json that represents data.
          this.json = getJSON()
        },
        editorProps: {
          // Open options menu.
          handleKeyDown: (view, event) => {
            if (event.key === "Tab") {
              // Get info for auto-complete pop-up menu.
              event.preventDefault();
              const cursorPosition = view.state.selection.anchor;
              const allText = view.dom.innerText;
              // Preset value of current imgs. 
              let currentImgs  = [];
              if (this.json.content){
                currentImgs = this.json.content.filter(obj =>  obj.type === "paragraph")[0].content.filter(obj =>  obj.type === "image").map(img => img.attrs.title);
              }
              this.handleOptions(cursorPosition, view, allText, currentImgs);
            }
          },
          handleTextInput: (view, from, to) => {
            // Learned from similar code: https://gitmemory.com/issue/scrumpy/tiptap/490/565634509.
            // For all char keys, to distinguish generated from user text.
            const [strike] = view.state.tr.selection.$anchor.marks();
            const isStrike = strike && strike.type.name === "strike";
            // If user writes inside genrated text.
            if (isStrike) {
              // Timeout to execute after the handler event.
              setTimeout(()=> {view.dispatch(view.state.tr.removeMark(from, to+1, strike));})
            }
            // To maintain the normal behavior of user input.
            return false;
          }
        }
      }),
      json : {},
    }
  },
  beforeDestroy() {
    this.editor.destroy();
  },
  methods: {
    getEditor(){
      return this.$refs.editor;
    },
    handleOptions(cursorPosition, view, allText, currentImgs){
      console.log("handleOptions: cursor | text | currentImgs",cursorPosition, allText, currentImgs);
      // Call two async api methods to autocomplete text and imgs,  in the meanwhile show loader bar.
      // this.handleImageInsert(cursorPosition, view); 
      this.handleTextInsert(cursorPosition, view); 

    },
    handleImageInsert(cursorPosition, view, imgId = "__CmMNKO4nw") {
      const node = view.state.schema.nodes.image.create({
        src: `unsplash25k/sketch_images/${imgId}.jpg`, 
        title: imgId});
    view.dispatch(view.state.tr.insert(cursorPosition, node));
    },
    handleTextInsert(cursorPosition,view, text="New text"){
      // Idea from https://www.gitmemory.com/issue/scrumpy/tiptap/385/515334522.
        const mark = view.state.schema.marks.strike.create();
        const transaction = view.state.tr.insertText(text + ' ');
        transaction.addMark(cursorPosition, cursorPosition + text.length, mark);
        view.dispatch(transaction);
    },
  },
};

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
