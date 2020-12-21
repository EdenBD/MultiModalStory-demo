<template>
  <div>
    <article>
      <editor-content ref="editorRef" :editor="editor" />
      <Options
        :isOpen="this.isOpen"
        :isLoading="this.isLoading"
        :top="this.top"
        :left="this.left"
        :texts="this.texts"
        :imgs="this.imgs"
        @text-insert="handleTextInsert"
        @img-insert="handleImageInsert"
      ></Options>
    </article>
    <!-- TODO(FORM submission database + free text form submission security issues) -->
    <RatingStory :submittedFormID="this.submittedFormID" @form-submit="handleFormSubmission"></RatingStory>
  </div>
</template>

<script lang="js">
// Import the basic building blocks
import { Editor, EditorContent } from "tiptap";
import Options from "./Options.vue";
import RatingStory from "./RatingStory.vue";

import Doc from "../nodes/Doc";
import Title from "../nodes/Title";
import Image from "../nodes/Image";


import { Placeholder, Strike,  TrailingNode, Link } from "tiptap-extensions";
import { API } from "../js/api/mainApi";


const api = new API();

export default {
  name: "Editor",
  components: {
    EditorContent,
    Options,
    RatingStory,
  },
  // setup() {
  //   this.api = new API();
  // },
  data() {
    return {
      // Default content. Editor is passed to `EditorContent` component as a `prop`.
      editor: new Editor({
        autofocus: 'end',
        disableInputRules: ["strike"],
        content: "<h2>The Mighty Dragon</h2><p><s>If you wish to follow my instructions, you must call the Dragon by name. The Dragon, you see, is the ruler of all Dragons. He is the ablest of all the living creatures, and because he is so strong, he has no doubt thought of taking pleasure in his beauty.</s><img src='unsplash25k/sketch_images1024/01zdIpN6uHU.jpg' id='01zdIpN6uHU'>However, </p>",
        extensions: [
          new Doc(),
          new Title(),
          new Strike(),
          new Image(),
          new Link(),
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
          // Change default story if route includes user's story id. 
          this.getInitialStory();
        },
        onUpdate: ({ getJSON, getHTML }) => {
          // Update json that represents data.
          this.json = getJSON();
          this.html = getHTML();
        },
        editorProps: {
          // Open options menu.
          handleKeyDown: (view, event) => { 
            // Check isLoading to prevent multiple keypresses from sending extra requests. 
            if (event.key === "Tab" && !this.isLoading) {
              // Get info for auto-complete pop-up menu.
              event.preventDefault();
              this.cursorPosition = view.state.selection.anchor;
              this.view = view;
              this.html = view.dom.innerHTML;
              // Get all text before the current cursor position.
              const allText = view.dom.innerText.substring(0, this.cursorPosition);
              // Find the screen coordinates (relative to top left corner of the window) of the given document position.
              const relativePosition = view.coordsAtPos(this.cursorPosition);
              // To avoid overflowing the Options menu and negative top values. 
              const cardWidth = 400; const presetHeight = 350;
              // To open card below text.
              const lineHeight = 10;
              this.top = Math.max(relativePosition.top + lineHeight, presetHeight), this.left = Math.min(relativePosition.left, window.innerWidth-cardWidth);
              // Get img from current HTML.
              const currentImgs  = this.getImgFromHTML(this.html);
              // If Alt,  perform slower text generation with re-ranking
              const quality = event.shiftKey;
              console.log("quality",quality);
              this.handleOptions(allText, currentImgs, quality);
            }
            else if (event.key == "Escape") {
              this.isOpen = false;
              this.isLoading = false;
            }
          },
          handleTextInput: (view, from) => {
            // Learned from similar code: https://gitmemory.com/issue/scrumpy/tiptap/490/565634509.
            // For all char keys, to distinguish generated from user text.
            const [strike] = view.state.tr.selection.$anchor.marks();
            const isStrike = strike && strike.type.name === "strike";
            // Update cursorPosition to insert text/ image in correct position.
            this.cursorPosition = view.state.selection.anchor + 1;
            // If user writes inside genrated text.
            if (isStrike) {
              // Timeout to execute after the handler event.
              setTimeout(()=> {view.dispatch(view.state.tr.removeMark(from, from+1, strike));})
            }
            // To maintain the normal behavior of user input.
            return false;
          },
        }
      }),
      // To get current imgs, and avoid duplicates in retreival. 
      json : {},
      html: "",
      view: {},
      cursorPosition: 0,
      // For Options - optional text and imgs.
      texts: ["1st Choice","2nd Choice","3rd Choice"],
      imgs: ["__G2yFuW7jQ", "ZzqM2YmqZ-o", "zZzKLzKP24o"],
      isLoading: false,
      isOpen: false,
      top: 0,
      left:0,
      submittedFormID: "",
    }
  },
  beforeDestroy() {
    this.editor.destroy();
  },
  methods: {
    getEditor(){
      return this.editor;
    },
    async shuffleStory(storyID){
      const storyHTML = await api.getStory(storyID);
      // If file not found, api returns "".
      if (storyHTML.length){
        this.editor.setContent(storyHTML, true);
      }
    },
    async getInitialStory() {
      const routeStoryId = this.$route.params.storyid;
      if (routeStoryId && routeStoryId !== "1"){
        // Get routeStoryId HTML from server.
        this.shuffleStory(routeStoryId)
      }
    },
    async handleOptions(allText, currentImgs, quality){
      this.isOpen = true;
      this.isLoading = true;
      // Get last numSenteces
      const numSenteces = 2;
      const extracts = allText.replace(/([.?!])\s*(?=[A-Z])/g, "$1|").split("|");
      const imagesExtract = extracts.slice(-numSenteces).join(" ");
      // Call backend
      this.texts = await api.postAutocompleteText(allText, quality);
      this.imgs = await api.postRetreiveImage(imagesExtract , currentImgs);
      // finished Loading
      this.isLoading = false;
      return false;
    },
    handleImageInsert(imgId) {
      this.isOpen = false;
      const node = this.view.state.schema.nodes.image.create({
        src: `unsplash25k/sketch_images1024/${imgId}.jpg`, 
        id: imgId});
      const transaction = this.view.state.tr.insert(this.cursorPosition, node);
      transaction.insertText(' ');
      this.view.dispatch(transaction);
      setTimeout(()=> {this.view.focus('end');});
    },
    handleTextInsert(text){
        this.isOpen = false;
        // Idea from https://www.gitmemory.com/issue/scrumpy/tiptap/385/515334522.
        const mark = this.view.state.schema.marks.strike.create();
        const transaction = this.view.state.tr.insertText(text+ ' ');
        transaction.addMark(this.cursorPosition, this.cursorPosition + text.length, mark);
        // transaction.setSelection(new TextSelection(this.cursorPosition + text.length));
        this.view.dispatch(transaction);
        setTimeout(()=> {this.view.focus('end');});

    },
    async handleFormSubmission(coherence, clarity, creativity, freeForm){
      // Send info from editor and form
      this.submittedFormID = "";
      this.submittedFormID = await api.postFormSubmission(coherence, clarity, creativity, freeForm, this.html)
      // Update URL according to submitted form URL
      this.$router.push({ name: "story", params: { storyid: this.submittedFormID } });
    },
    getImgFromHTML(html){
      const el = document.createElement( 'html' );
      el.innerHTML = html;
      const imgTags = el.getElementsByTagName( 'img' ); 
      return Array.prototype.map.call(imgTags, obj => obj.id)
    }
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
