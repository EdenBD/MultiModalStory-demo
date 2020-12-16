<template>
  <div v-show="isOpen" class="options-popup" v-bind:style="{'left': left +'px'}">
    <v-progress-circular indeterminate color="primary" v-show="isLoading"></v-progress-circular>
    <v-card max-width="22em" class="mx-auto" v-show="!isLoading">
      <v-list>
        <v-list-item-group>
          <!--     Text Row     -->
          <v-list-item
            v-for="(text, index) in texts"
            :key="index"
            @click="$emit('text-insert', text)"
          >
            <v-list-item-icon>
              <v-icon>mdi-text</v-icon>
            </v-list-item-icon>
            <v-list-item-title v-text="text" style="{'padding-left': '0.1em';}"></v-list-item-title>
          </v-list-item>
        </v-list-item-group>
        <!--     Images Row     -->
        <v-list-item-group class="options-imgs">
          <v-list-item-icon>
            <v-icon class="options-imgs-icon">mdi-image</v-icon>
          </v-list-item-icon>
          <v-list-item
            v-for="(img, index) in imgs"
            :key="index+texts.length"
            @click="$emit('img-insert', img)"
            class="options-img"
          >
            <v-list-item-title>
              <v-img :src="'unsplash25k/sketch_images/' + img +'.jpg'"></v-img>
            </v-list-item-title>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-card>
  </div>
</template>

<script lang="js">
export default {
  name: "Options",
  props: {
    isOpen: Boolean,
    isLoading: Boolean,
    // bottom: Number,
    left: Number,
    texts: Array,
    imgs: Array},
};
</script>

