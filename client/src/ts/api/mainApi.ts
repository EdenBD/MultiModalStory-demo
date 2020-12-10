import * as d3 from "d3";
import { makeUrl, toPayload } from "../etc/apiHelpers";
import { URLHandler } from "../etc/URLHandler";

const baseurl = URLHandler.basicURL();

export interface Story {
    texts: string[];
    images: any[];
}

export class API {
    constructor(private baseURL: string | null = null) {
        if (this.baseURL == null) {
            this.baseURL = baseurl + "/api";
        }
    }

    /**
     * Call MultiModal StoryGenerator to create a text-and-images story according to a given title.
     *
     * @param title
     */
    generateStoryByTitle(title: string): Promise<Story> {
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
     *
     * @param extract
     * @param currentImgs
     */
    retreiveImagesByExtract(extract: string, currentImgs: Array<string> = []): Promise<Array<string>> {
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
     *
     * @param extracts
     */
    autocompleteTextByAllExtracts(extracts: string): Promise<Array<string>> {
        const toSend = {
            extracts: extracts
        };

        const url = makeUrl(this.baseURL + "/get-text", toSend);
        console.log("--- GET " + url);

        return d3.json(url);
    }
}
