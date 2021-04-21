<template>
  <div
    v-show="isOpen"
    class="options-popup"
    v-bind:style="{ left: left + 'px', top: top + 'px' }"
  >
    <div class="loader" v-show="isLoading"></div>
    <!-- Update Editor: cardWidth in case of changing max-width.-->
    <v-card
      max-width="400px"
      class="mx-auto"
      v-show="!isLoading"
      v-click-outside="onClickOutside"
    >
      <v-list>
        <v-list-item-group>
          <!--     Text Row     -->
          <div v-for="(text, index) in texts" :key="index">
            <v-list-item v-if="text.length" @click="$emit('text-insert', text)">
              <v-list-item-icon>
                <v-icon>mdi-text</v-icon>
              </v-list-item-icon>
              <v-list-item-title v-text="text"></v-list-item-title>
            </v-list-item>
          </div>
        </v-list-item-group>
        <!--     Images Row     -->
        <v-list-item-group class="options-imgs">
          <v-list-item-icon>
            <v-icon class="options-imgs-icon">mdi-image</v-icon>
          </v-list-item-icon>
          <v-list-item
            v-for="(img, index) in imgs"
            :key="index + texts.length"
            @click="$emit('img-insert', img)"
            class="options-img"
            :class="styling"
          >
            <v-list-item-title>
              <v-img :src="`${images_path}${img}/90x90`"></v-img>
            </v-list-item-title>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-card>
  </div>
</template>

<script lang="js">
import Constants from "./Constants";

export default {
  name: "Options",
  props: {
    isOpen: Boolean,
    isLoading: Boolean,
    top: Number,
    left: Number,
    texts: Array,
    imgs: Array,
    styling: String},
  data: () => ({
    images_path: Constants.IMAGE_PATH,
  }),
  methods: {
    onClickOutside () {
      // If Options card is open, and user clicks outside card - close it.
      if (!this.isLoading && this.isOpen) {
        this.$emit('close-options');
      }
    },
  },
};
</script>

