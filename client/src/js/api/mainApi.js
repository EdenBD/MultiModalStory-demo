import * as d3 from "d3";
import { makeUrl, toPayload } from "../etc/apiHelpers";
import { URLHandler } from "../etc/URLHandler";



export class API {
    constructor(baseURL = null) {
        this.baseURL = baseURL;
        if (this.baseURL == null) {
            const baseurl = URLHandler.basicURL();
            this.baseURL = baseurl + "/api";
        }
    }

    // Options bar.

    /**
     * Call MultiModal StoryGenerator to retreive non-duplicate images according to given extract and current images ids.
     * Returns: Promise<Array<string>>
     * @param extract
     * @param current
     */
    postRetreiveImage(extract, current) {
        const toSend = {
            extract: extract,
            current: current,
        }

        const url = makeUrl(this.baseURL + '/post-autocomplete-img');
        const payload = toPayload(toSend)

        console.log("--- POST " + url, payload);

        return d3.json(url, payload)
    }

    /**
     * Call MultiModal StoryGenerator to generate text from given extracts 
     * (simple generation with/out one re-ranking round depending on quality true/false).
     * Returns  Promise<Array<string>>
     * @param extracts
     * @param quality
     */
    postAutocompleteText(extracts, quality) {
        const toSend = {
            extracts: extracts,
            quality: quality,
        }

        const url = makeUrl(this.baseURL + '/post-autocomplete-text');
        const payload = toPayload(toSend)

        console.log("--- POST " + url, payload);

        return d3.json(url, payload)
    }
}
