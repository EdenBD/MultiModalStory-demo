import * as d3 from "d3";
import { makeUrl } from "../etc/apiHelpers";
import { URLHandler } from "../etc/URLHandler";



export class API {
    constructor(baseURL = null) {
        this.baseURL = baseURL;
        if (this.baseURL == null) {
            const baseurl = URLHandler.basicURL();
            this.baseURL = baseurl + "/api";
        }
    }

    /**
     * Call MultiModal StoryGenerator to create a text-and-images story according to a given title.
     * Returns Promise<Array<string>, Array<string>>
     * @param title
     */
    generateStoryByTitle(title) {
        const toSend = {
            title: title
        };

        const url = makeUrl(this.baseURL + "/get-a-story", toSend);
        console.log("--- GET " + url);

        return d3.json(url);
    }

    // Options bar.

    /**
     * Call MultiModal StoryGenerator to retreive non-duplicate images according to given extract and current images ids.
     * Returns: Promise<Array<string>>
     * @param extract
     * @param currentImgs: Array<string> = []
     */
    retreiveImagesByExtract(extract, currentImgs = []) {
        const toSend = {
            extract: extract,
            currentImgs: currentImgs
        };

        const url = makeUrl(this.baseURL + "/get-image", toSend);
        console.log("--- GET " + url);

        return d3.json(url);
    }

    /**
     * Call MultiModal StoryGenerator to generate text from given extracts (simple generation wihtout re-ranking).
     * Returns  Promise<Array<string>>
     * @param extracts
     */
    autocompleteTextByAllExtracts(extracts) {
        const toSend = {
            extracts: extracts
        };

        const url = makeUrl(this.baseURL + "/get-text", toSend);
        console.log("--- GET " + url);

        return d3.json(url);
    }
}
