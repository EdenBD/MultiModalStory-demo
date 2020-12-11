<template>
  <article class="ratings-card">
    <h3 class="card-title">Score Auto-Generated Story</h3>
    <form id="scores" action="#" method="post">
      <!-- CLARITY: readability, simplicity, coherence -->
      <div>
        <h4 class="card-title rating-el-title-el">Clarity</h4>
        <div class="rating-el-title-el star-rating">
          <fieldset>
            <!-- same name attributes ensures users can only choose one star -->
            <input type="radio" id="clarity-star5" name="clarity-rating" value="5" />
            <label for="clarity-star5" title="Outstanding">5 stars</label>
            <input type="radio" id="clarity-star4" name="clarity-rating" value="4" />
            <label for="clarity-star4" title="Very Good">4 stars</label>
            <input type="radio" id="clarity-star3" name="clarity-rating" value="3" />
            <label for="clarity-star3" title="Good">3 stars</label>
            <input type="radio" id="clarity-star2" name="clarity-rating" value="2" />
            <label for="clarity-star2" title="Poor">2 stars</label>
            <input type="radio" id="clarity-star1" name="clarity-rating" value="1" />
            <label for="clarity-star1" title="Very Poor">1 star</label>
          </fieldset>
        </div>
      </div>
      <!-- COHERENCY: tale like, diversity -->
      <div>
        <h4 class="card-title rating-el-title-el">Coherence</h4>
        <div class="rating-el-title-el star-rating">
          <fieldset>
            <input type="radio" id="coherence-star5" name="coherence-rating" value="5" />
            <label for="coherence-star5" title="Outstanding">5 stars</label>
            <input type="radio" id="coherence-star4" name="coherence-rating" value="4" />
            <label for="coherence-star4" title="Very Good">4 stars</label>
            <input type="radio" id="coherence-star3" name="coherence-rating" value="3" />
            <label for="coherence-star3" title="Good">3 stars</label>
            <input type="radio" id="coherence-star2" name="coherence-rating" value="2" />
            <label for="coherence-star2" title="Poor">2 stars</label>
            <input type="radio" id="coherence-star1" name="coherence-rating" value="1" />
            <label for="coherence-star1" title="Very Poor">1 star</label>
          </fieldset>
        </div>
      </div>
      <!-- CREATIVITY: tale like, diversity -->
      <div>
        <h4 class="card-title rating-el-title-el">Creativity</h4>
        <div class="rating-el-title-el star-rating">
          <fieldset>
            <input type="radio" id="creativity-star5" name="creativity-rating" value="5" />
            <label for="creativity-star5" title="Outstanding">5 stars</label>
            <input type="radio" id="creativity-star4" name="creativity-rating" value="4" />
            <label for="creativity-star4" title="Very Good">4 stars</label>
            <input type="radio" id="creativity-star3" name="creativity-rating" value="3" />
            <label for="creativity-star3" title="Good">3 stars</label>
            <input type="radio" id="creativity-star2" name="creativity-rating" value="2" />
            <label for="creativity-star2" title="Poor">2 stars</label>
            <input type="radio" id="creativity-star1" name="creativity-rating" value="1" />
            <label for="creativity-star1" title="Very Poor">1 star</label>
          </fieldset>
        </div>
      </div>
      <h4 class="card-title rating-el-title-el">Any comments, questions or suggestions?</h4>
      <textarea rows="3"></textarea>
      <div class="submit-bttn card-title">
        <input type="submit" value="Submit Story" />
      </div>
    </form>
  </article>
</template>

<script lang="ts">
export default {
  name: "RatingForm"
};
</script>

