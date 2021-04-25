<template>
  <!-- MAIN EDITOR -->
  <div>
    <Header ref="childHeader" @shuffle-story="handleShuffleStory"></Header>
    <div class="editor">
      <article class="main">
        <transition name="fade">
          <div class="float-info bounce-6" v-if="showTabPrompt">Press <i class="fa fa-magic" aria-hidden="true"></i>
                <code style="font-weight: 900">tab</code> to autocomplete</div>
        </transition>
        <editor-content ref="editorRef" :editor="editor" />
        <Options
          :isOpen="this.isOpen"
          :isLoading="this.isLoading"
          :top="this.top"
          :left="this.left"
          :texts="this.texts"
          :imgs="this.imgs"
          :styling="this.styling"
          @text-insert="handleTextInsert"
          @img-insert="handleImageInsert"
          @close-options="handleClosingOptions"
        ></Options>
      </article>
      <RatingStory
        :submittedFormID="this.submittedFormID"
        :isSubmitPressed="this.isSubmitPressed"
        @form-submit="handleFormSubmission"
        :showContent="this.hasSomeContent"
      ></RatingStory>
    </div>
  </div>
</template>

<script lang="js">
// Import the basic building blocks
import { Editor, EditorContent } from "tiptap";
import Options from "./Options.vue";
import RatingStory from "./RatingStory.vue";
import Header from "./Header.vue";

import Doc from "../nodes/Doc";
import Title from "../nodes/Title";
import Image from "../nodes/Image";
import Constants from "./Constants";

import { Placeholder, Strike,  TrailingNode, Link } from "tiptap-extensions";
import { API } from "../js/api/mainApi";

const api = new API();

// Taken from https://stackoverflow.com/questions/11935175/sampling-a-random-subset-from-an-array/19631135
function sample(array, size) {
  const results = [],
    sampled = {};
  while(results.length<size && results.length<array.length) {
    const index = Math.trunc(Math.random() * array.length);
    if(!sampled[index]) {
      results.push(array[index]);
      sampled[index] = true;
    }
  }
  return results;
}

export default {
  name: "Editor",
  components: {
    EditorContent,
    Options,
    RatingStory,
    Header,
  },
  data() {
    return {
      // Default content. Editor is passed to `EditorContent` component as a `prop`.
      editor: new Editor({
        autofocus: 'end',
        disableInputRules: ["strike"],
        content: "",
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
              return "Click to write something awesome...";
            }
          })
        ],
        onInit: ({ view }) => {
          localStorage.clear()

          // Log view once the editor is initialized.
          this.view = view;
          // Change default story if route includes user's story id. 
          this.getInitialStory();
        },
        onUpdate: ({ getJSON, getHTML }) => {
          // Update json that represents data.
          this.json = getJSON();
          this.html = getHTML();

          const editorContentLength = this.editor.view.dom.innerText.trim().length
          this.hasSomeContent = editorContentLength > 0
        },
        editorProps: {
          // Open options menu.
          handleKeyDown: (view, event) => { 
            // Check isLoading to prevent multiple keypresses from sending extra requests. 
            const devComplete = event.ctrlKey && event.key == " "
            const requestAutocomplete = event.key == "Tab" || devComplete
            if (requestAutocomplete && !this.isLoading ) {
              // Get info for auto-complete pop-up menu.
              event.preventDefault();
              this.cursorPosition = view.state.selection.anchor;
              this.view = view;
              this.html = view.dom.innerHTML;
              // Get all text before the current cursor position.
              const allText = view.dom.innerText.substring(0, this.cursorPosition);
              // Find the screen coordinates (relative to top left corner of the window) of the given document position.
              const relativePosition = view.coordsAtPos(this.cursorPosition);
              // To open card below text.
              const lineHeight = 10; const loadingHeight = 40;
              // To show loading sign even if pressed below current window. 
              this.top = Math.min(relativePosition.top + lineHeight, window.innerHeight-loadingHeight);
              this.left = relativePosition.left;
              // To avoid incorrect top, left values after image insertions.
              const positionError = 50;
              if (this.top < positionError) {
                const presetHeight = window.innerHeight/2+150; const presetWidth = window.innerWidth/2;
                this.top = presetHeight; this.left = presetWidth;
              }
              // Get img from current HTML.
              const currentImgs  = this.getImgFromHTML(this.html);
              // If HQ on,  performs slower text generation with re-ranking
              const quality = this.$refs.childHeader.isHQAutocompleteOn();
              this.handleOptions(allText, currentImgs, quality);
              this.hasAutocompleted = true
            }
            else if (event.key == "Escape") {
              this.isOpen = false;
              this.isLoading = false;
            }
          },
          handleTextInput: (view, from) => {
            // Learned from similar code: https://gitmemory.com/issue/scrumpy/tiptap/490/565634509.

            // Was the last input in the body of the story? This has a bug and looks at two inputs ago
            this.lastInputWasInBody = view.trackWrites?.parentElement?.nodeName == 'P'
            console.log(view)

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
      imgs: ["HxhSVDapt-I", "h2LMXbpvwCw", "I9EhRx3oQ7Q"],
      isLoading: false,
      isOpen: false,
      top: 0,
      left:0,
      submittedFormID: "",
      isSubmitPressed: false,
      styling: "none",
      hasSomeContent: false,
      hasAutocompleted: false,
      lastInputWasInBody: false
    }
  },
  beforeDestroy() {
    this.editor.destroy();
  },
  computed: {
    showTabPrompt() {
      return !this.hasAutocompleted && this.hasSomeContent && this.lastInputWasInBody
    }
  },
  methods: {
    getEditor(){
      return this.editor;
    },
    async handleShuffleStory(storyID){
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
        this.handleShuffleStory(routeStoryId)
      }
    },
    async handleOptions(allText, currentImgs, quality){
      // Update Options props
      this.isOpen = true;
      this.isLoading = true;
      this.styling = this.$refs.childHeader.currentStyling();
      if (allText.trim().length){
        // Get last numSenteces
        const numSenteces = 2;
        const extracts = allText.replace(/([.?!])\s*(?=[A-Z])/g, "$1|").split("|");
        const imagesExtract = extracts.slice(-numSenteces).join(" ");
        // Call backend
        this.imgs = await api.postRetreiveImage(imagesExtract , currentImgs);
        this.texts = await api.postAutocompleteText(allText, quality);

      }
      // If editor is empty, return preset titles and images.
      else {
        this.texts = sample(Constants.PRESET_TITLES, 3);
        this.imgs = sample(Constants.PRESET_IMG_IDS, 3);
      }
      // finished Loading
      this.isLoading = false;
      // Fix card position if beyond window borders.
      const cardHeight = 300; const cardWidth = 400; 
      this.top = Math.min(this.top, window.innerHeight-cardHeight);
      this.left = Math.min(this.left, window.innerWidth-cardWidth); 
      return false;
    },
    handleClosingOptions() {
      this.isOpen = false;
    },
    handleImageInsert(imgId) {
      this.isOpen = false;
      const node = this.view.state.schema.nodes.image.create({
        src: `${Constants.IMAGE_PATH}${imgId}/256x256`, 
        id: imgId, class: this.styling});
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
      // Disable submit button during submission.
      this.isSubmitPressed = true;
      this.submittedFormID = await api.postFormSubmission(coherence, clarity, creativity, freeForm, this.html)
      this.isSubmitPressed = false;
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

article {
  position: static;
}

.float-info {
  position: absolute;
  right: 0.5rem;
  padding: inherit;
  top: 1rem;
  transform-origin: bottom;
  animation-duration: 2s;
  animation-iteration-count: infinite;
}

.bounce-6 {
    animation-name: bounce-6;
    animation-timing-function: ease;
}
@keyframes bounce-6 {
    0%   { transform: scale(1,1)      translateY(0); }
    10%  { transform: scale(1.03,.97)   translateY(0); }
    30%  { transform: scale(.97,1.03)   translateY(-3px); }
    50%  { transform: scale(1.01,.99) translateY(0); }
    57%  { transform: scale(1,1)      translateY(-1px); }
    64%  { transform: scale(1,1)      translateY(0); }
    100% { transform: scale(1,1)      translateY(0); }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>
