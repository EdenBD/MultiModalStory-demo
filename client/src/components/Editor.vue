<template>
  <article>
    <editor-content ref="editorRef" :editor="editor" />
    <Options
      :isOpen="this.isOpen"
      :isLoading="this.isLoading"
      :bottom="this.bottom"
      :left="this.left"
      :texts="this.texts"
      :imgs="this.imgs"
      @text-insert="handleTextInsert"
      @img-insert="handleImageInsert"
    ></Options>
  </article>
</template>

<script lang="js">
// Import the basic building blocks
import { Editor, EditorContent } from "tiptap";
import Options from "./Options.vue";
import Doc from "../nodes/Doc";
import Title from "../nodes/Title";
import { Placeholder, Strike, Image,  TrailingNode } from "tiptap-extensions";
import { API } from "../js/api/mainApi";
const api = new API();

export default {
  name: "Editor",
  components: {
    EditorContent,
    Options,
  },
  setup() {
    this.api = new API();
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
        onInit: ({ view }) => {
          // Log view once the editor is initialized.
          this.view = view;
        },
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
              this.cursorPosition = view.state.selection.anchor;
              this.view = view;
              const allText = view.dom.innerText;
              // Get screen coordinates
              const absolutePosition = view.coordsAtPos(this.cursorPosition);
              // Add card size to open mrenu below text.
              const cardSize = 200;
              this.bottom = absolutePosition.bottom + cardSize, this.left = absolutePosition.left;
              // Preset value of current imgs. 
              let currentImgs  = [];
              if (this.json.content){
                currentImgs = this.json.content.filter(obj =>  obj.type === "paragraph")[0].content.filter(obj =>  obj.type === "image").map(img => img.attrs.title);
              }
              this.handleOptions(allText, currentImgs);
            }
            else if (event.key == "Escape") {
              this.isOpen = false;
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
      // To get current imgs, and avoid duplicates in retreival. 
      json : {},
      view: {},
      cursorPosition: 0,
      // For Options - optional text and imgs.
      texts: ["1st Choice","2nd Choice","3rd Choice"],
      imgs: ["__G2yFuW7jQ", "ZzqM2YmqZ-o", "zZzKLzKP24o"],
      isLoading: false,
      isOpen: false,
      bottom: 0,
      left:0,
    }
  },
  beforeDestroy() {
    this.editor.destroy();
  },
  methods: {
    getEditor(){
      return this.editor;
    },
    focus(){
      if (this.view.length) {     
        console.log("focus");
        this.editor.focus('end')
      }
    },
    shuffleStory(){
      this.editor.setContent("text", true);
    },
    async handleOptions(allText, currentImgs){
      this.isOpen = true;
      this.isLoading = true;
      // Get last numSenteces
      const numSenteces = 2;
      const extracts = allText.replace(/([.?!])\s*(?=[A-Z])/g, "$1|").split("|");
      const imagesExtract = extracts.slice(-numSenteces).join(" ");
      // Call backend
      this.texts = await api.postAutocompleteText(allText);
      this.imgs = await api.postRetreiveImage(imagesExtract , currentImgs);
      // finished Loading
      this.isLoading = false;
      return false;
    },
    handleImageInsert(imgId) {
      this.isOpen = false;
      const node = this.view.state.schema.nodes.image.create({
        src: `unsplash25k/sketch_images/${imgId}.jpg`, 
        title: imgId});
    this.view.dispatch(this.view.state.tr.insert(this.cursorPosition, node));
    this.view.focus('end');
    },
    handleTextInsert(text){
        this.isOpen = false;
        // Idea from https://www.gitmemory.com/issue/scrumpy/tiptap/385/515334522.
        const mark = this.view.state.schema.marks.strike.create();
        const transaction = this.view.state.tr.insertText(text+ ' ');
        transaction.addMark(this.cursorPosition, this.cursorPosition + text.length, mark);
        this.view.dispatch(transaction);
        this.view.focus('end');

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
