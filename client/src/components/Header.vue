<template>
  <div>
    <!-- HEADER + OPTION BAR -->
    <header class="sticky">
      <div class="inner-heading">
        <div class="header-el">
          <img class="logo" src="bear.svg" />
        </div>
        <div class="header-el">
          <a
            href="https://github.com/EdenBD/MultiModalStory-demo"
            target="_blank"
            data-title="Uses GPT-2 & Unsplash Images to generate text-and-images stories"
          >
            <img class="title-logo shadow" src="logo2.png" />
          </a>
          <div class="options">
            <!-- Shuffle Story -->
            <div class="options-el clickable">
              <a @click.prevent="shuffleStory">
                <i class="fa fa-random" aria-hidden="true"></i> Shuffle Story
              </a>
            </div>
            <!-- Autocomplete -->
            <div class="options-el shadow clean-format">
              <a data-title="Generates up to three text completions and images">
                <i class="fa fa-magic" aria-hidden="true"></i>
                <code>tab</code> for
                <strong>Autocomplete</strong>
                <span class="timing">(2 sec)</span>
              </a>
            </div>
            <!-- High-Quality Autocomplete -->
            <div class="options-el shadow clean-format">
              <v-switch
                v-model="highQualityAutocomplete"
                class="clean-switch ma-0 pa-0"
                hide-details
                color="#57ce5b"
              >
              </v-switch>
              <a
                data-title="Returns top-ranked texts according to creativity, readability, coherency, and positivity measures"
              >
                <strong class="clean-switch"> High-Quality Autocomplete</strong>
                <span class="timing clean-switch">(5 sec)</span>
              </a>
            </div>
            <!--     Image Style Transfer     -->
            <div class="options-el shadow clean-format">
              <a
                data-title="Changes inserted images' style. Applies no styling by default"
              >
                <strong class="header-style">Image Style</strong>
              </a>
              <div class="header-imgs">
                <v-btn-toggle
                  v-model="chosen_style"
                  color="#00FF00"
                  dense
                  borderless
                >
                  <v-btn
                    v-for="(style, index) in styles"
                    :key="index"
                    x-large
                    fab
                    tile
                    class="header-btn-img"
                  >
                    <v-avatar tile size="55">
                      <img
                        src="none.png"
                        class="header-style-img"
                        :class="style"
                      />
                    </v-avatar>
                  </v-btn>
                </v-btn-toggle>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- DESCRIPTION -->
    <div class="description">
      <div class="desciption-txt">
        <b>Step 1:</b> <a @click.prevent="shuffleStory">Shuffle initial story</a> or start writing.
        <br />
        <b>Step 2:</b> Press <i class="fa fa-magic" aria-hidden="true"></i>
                <code style="font-weight: 900">tab</code> to autocomplete text and images.
        <br />
        <b>Step 3:</b> Give feedback and submit your story.
      </div>
    </div>
  </div>
</template>

<script lang="js">
import Constants from "./Constants";


export default {
  name: "Header",
    data: function () {
    return {
      highQualityAutocomplete: false,
      styles: ['none', 'sepia', 'sketch', 'invert'],
      // Index Corresponds to list of styles
      chosen_style: 0,
      storyID: this.$route.params.storyid || "1",
    };
  },
    watch: {
    $route() {
      this.storyID = this.$route.params.storyid;
    },
  },
  methods: {
    isHQAutocompleteOn(){
      return this.highQualityAutocomplete;
    },
    currentStyling(){
      return this.styles[this.chosen_style]
    },
    shuffleStory: function () {
    // User called shuffle story from default story
    if (this.storyID.length === 1) {
      // Once tried all default stories, return to default storyID=1.
      this.storyID = (
        (Number(this.storyID) % Constants.NUM_PRESET_STORIES) +
        1
      ).toString();
      // User called shuffle after submitting a form
    } else {
      this.storyID = "2";
    }
    // Update the route.
    this.$router.push({ name: "story", params: { storyid: this.storyID } });
    // Update the editor content.
    this.$emit('shuffle-story', this.storyID);
    // this.$refs.childEditor.shuffleStory();
  },
  }
};
</script>

