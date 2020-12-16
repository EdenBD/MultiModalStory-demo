<template>
  <v-form v-model="valid" ref="form">
    <v-container>
      <h3 class="card-main-title">Score Auto-Generated Story</h3>
      <v-row>
        <v-col cols="12" md="4">
          <h4 class="card-title rating-el-title-el">Clarity</h4>
          <v-rating
            v-model="clarity"
            background-color="orange lighten-3"
            color="orange"
            large
            :rules="ratingRules"
            half-increments
          ></v-rating>
        </v-col>

        <v-col cols="12" md="4">
          <h4 class="card-title rating-el-title-el">Coherence</h4>
          <v-rating
            v-model="coherence"
            background-color="orange lighten-3"
            color="orange"
            large
            :rules="ratingRules"
            half-increments
          ></v-rating>
        </v-col>

        <v-col cols="12" md="4">
          <h4 class="card-title rating-el-title-el">Creativity</h4>
          <v-rating
            v-model="creativity"
            background-color="orange lighten-3"
            color="orange"
            large
            :rules="ratingRules"
            half-increments
          ></v-rating>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" md="12">
          <v-text-field v-model="free" label="Any Comments, Questions or Suggestions"></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" md="12">
          <v-checkbox
            v-model="checkbox"
            :rules="[v => !!v || 'You must agree to continue!']"
            label="Do you agree to submit your feedback and story for research?"
            required
          ></v-checkbox>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" md="4">
          <v-btn :disabled="!valid" class="mr-4" @click="submit">Submit Story</v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script lang="js">
export default {
  name: "RatingStory",
  data: () => ({
  valid: false,
  coherence: 2.5,
  clarity: 2.5,
  creativity: 2.5,
  ratingRules: [
    v => !!v || 'Rating is required',
  ],
  free: '',
  checkbox: false,
}),
methods: {
      submit () {
        // Get all form data and editor JSON and save in directory.
        this.$refs.form.validate()
      },
    },
};
</script>

