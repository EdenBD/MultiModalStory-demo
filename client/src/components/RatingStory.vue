<template>
  <v-form v-model="valid" ref="form">
    <v-container>
      <h3 class="card-main-title">Score Auto-Generated Story</h3>
      <v-row>
        <v-col cols="12" md="4">
          <a class="clean-format" data-title="Easy to understand">
            <h4 class="card-title rating-el-title-el">Clarity</h4>
          </a>
          <v-rating
            v-model="clarity"
            background-color="orange lighten-3"
            color="orange"
            large
            half-increments
          ></v-rating>
        </v-col>
        <v-col cols="12" md="4">
          <a class="clean-format" data-title="Follows a consistent theme">
            <h4 class="card-title rating-el-title-el">Coherence</h4>
          </a>
          <v-rating
            v-model="coherence"
            background-color="orange lighten-3"
            color="orange"
            large
            half-increments
          ></v-rating>
        </v-col>
        <v-col cols="12" md="4">
          <a class="clean-format" data-title="Engaging and interesting to read">
            <h4 class="card-title rating-el-title-el">Creativity</h4>
          </a>
          <v-rating
            v-model="creativity"
            background-color="orange lighten-3"
            color="orange"
            large
            half-increments
          ></v-rating>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" md="12">
          <v-text-field
            v-model="free"
            label="Any Comments, Questions or Suggestions"
            maxlength="150"
            counter
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" md="12">
          <v-checkbox
            v-model="checkbox"
            :rules="[v => !!v || 'You must agree to submit!']"
            label="Do you agree to submit your feedback and publish your story?"
            required
          ></v-checkbox>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" md="8">
          <v-alert
            v-show="submittedFormID && submittedFormID.length !== 0"
            dense
            outlined
            dismissible
            class="alert"
          >
            <span>
              Thank you!
              <br />Successfully Published Story :D
            </span>
            <ShareStory></ShareStory>
          </v-alert>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" md="4">
          <v-btn :disabled="!valid" class="story-submit" @click="submit">Submit Story</v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script lang="js">
import ShareStory from "./ShareStory.vue";

export default {
  name: "RatingStory",
    components: {
    ShareStory,
  },
  emits: [
    "form-submit",
  ],
  props: {
    submittedFormID: String,
  },
  data: () => ({
  valid: false,
  coherence: 0,
  clarity: 0,
  creativity: 0,
  free: '',
  checkbox: false,
}),
methods: {
      submit () {
        // Get all form data and editor JSON and save in directory.
        this.$refs.form.validate();
        this.$emit("form-submit", this.coherence, this.clarity, this.creativity, this.free);
      },
    },
};
</script>

