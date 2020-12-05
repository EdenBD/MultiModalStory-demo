import * as d3 from 'd3'
import { SimpleEventHandler } from './etc/SimpleEventHandler'
import { API } from "./api/mainApi"
import { AnyMxRecord } from 'dns';

/**
 * Main functionality in the below function
 */
export function main() {
    const api = new API()

    // const mainDiv = document.getElementById('main')
    // const wl = new HTMLList(mainDiv, eventHandler)
    // Form ratings

    // var clarity = d3.select('input[name="clarity-rating"]:checked').property("value");
    // var creativity = d3.select('input[name="creativity-rating"]:checked').property("value");
    // var engagement = d3.select('input[name="engagement-rating"]:checked').property("value");
    // console.log(`clarity  val: ${clarity}`);

    const title_txt = d3.select('#story-title').text();

    // TODO(Change to call by onClick)
    // api.generateStoryByTitle(title_txt).then((story) => {
    //     // Create <p> story.texts[i] </p>
    //     // Length of sory.texts is determined by constants.NUM_IMAGES_PER_STORY = 2
    //     for (let i = 0; i < story.texts.length; i++) {
    //         d3.select(`#story-p${i}`)
    //             .text(story.texts[i])
    //             .attr("class", "editable")
    //             .attr("contenteditable", "true");

    //         // Create <img src="data:image/jpg;base64,' + story.images[i] + ' />
    //         d3.select(`#story-img${i}`)
    //             // sketch_images determines using sketch style transfer for images. 
    //             .attr("src", `unsplash25k/sketch_images/${story.images[i]}.jpg`)
    //             .attr("class", "story-img");
    //     }
    // })

    // TODO(Change current_p to onClick of autocompletion request/ tab d3.select(this))
    // let current_selection
    const current_p = d3.select('#story-p1');
    // Remove multiple spaces 
    const p_text = current_p.text().replace(/\s\s+/g, ' ');
    // api.retreiveImagesByExtract(p_text).then((img_ids) => {
    //     for (let i = 0; i < img_ids.length; i++) {
    //         // TODO(append imgs to options bar)
    //         current_p.append("img")
    //             .attr("src", `unsplash25k/sketch_images/${img_ids[i]}.jpg`)
    //             .attr("class", "story-img");
    //     }
    // });

    // Get all paragraphs texts. 
    let allText = ''
    const pNodes = d3.selectAll("p").text();
    console.log('pNodes', pNodes)

    // .each(function (d, i) {
    //     var pText = d3.selectAll(this.childNodes);
    //     allText += pText.text().replace(/\s\s+/g, ' ');
    // });
    // Append generated texts. 
    // api.autocompleteTextByAllExtracts(allText).then((text_completions) => {
    //     for (let i = 0; i < text_completions.length; i++) {
    //         // TODO(append texts to options bar)
    //         current_p.append("span")
    //             .text(text_completions[i])
    //             .attr("class", "editable");
    //     }
    // });

    // Event handler on change of rating value:
    // const clarity_all = d3.selectAll('input[name="clarity-rating"]');
    // clarity_all.on('change', function (d) { console.log('clarity changed to ' + this.value); });
    /**
     * Binding the event handler
     */
    // eventHandler.bind(HTMLList.events.click, (d) => console.log(`${d.name} was clicked!`))
    // eventHandler.bind(HTMLList.events.mouseOver, (d) => console.log(`${d.name} was moused Over!`))

    // const data = ["cont", "data", "to", "change"]

    // wl.update(data)
}