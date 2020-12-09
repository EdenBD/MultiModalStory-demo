<template>
  <article>
    <!-- TODO(ADD onClick Change story)-->
    <!-- TODO(ADD text autocompletion _sample_sequence onClick + keyboard) -->
    <!-- TODO(ADD image retrieval generate_images(texts_to_consider=1, one_image_retrival=True) onClick + keyboard) -->
    <!-- TODO(FORM submission database + free text form submission security issues) -->
    <!-- TODO(Loading symbol, progresss according to total time? Completed steps?) -->
    <div id="story-article" contenteditable="true" class="editable" v-html="HTMLcontent"></div>
  </article>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "VEditor",
  data: () => ({
    HTMLcontent: `<h2 class="editable story-title" contenteditable="true" id="story-title">The Mighty Dragon</h2><p></p><p><s>This creature, the Mighty Dragon, lived hundreds of years, rising in the clouds above the world and his great body slowly sinking beneath the earth. His power was greater than all the dragons on Mount Fuji, as his body held more power than all the dragons in the world.</s></p><img class="story-img" src="unsplash25k/sketch_images/pWzcj7wnC-c.jpg" id="pWzcj7wnC-c" /><p>CONTINUE STORY HERE/ THE END.</p>`
  })
});
</script>

