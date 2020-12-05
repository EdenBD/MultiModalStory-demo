import * as d3 from 'd3';
import { makeUrl, toPayload } from '../etc/apiHelpers'
import { URLHandler } from '../etc/URLHandler';


const baseurl = URLHandler.basicURL()

export class Story {

    public readonly texts: Array<string>;
    // images is  an array of tuples
    public readonly images: Array<any>;

}

export class API {

    constructor(private baseURL: string = null) {
        if (this.baseURL == null) {
            this.baseURL = baseurl + '/api';
        }
    }

    /**
     * Example API call, typed with expected response
     *
     * @param firstname
     */
    getAHi(firstname: string): Promise<string> {
        const toSend = {
            firstname: firstname
        }

        const url = makeUrl(this.baseURL + "/get-a-hi", toSend)
        console.log("--- GET " + url);

        return d3.json(url)
    }

    /**
     * Example POST request, typed with expected response
     * 
     * @param firstname
     */
    postABye(firstname: string): Promise<string> {
        const toSend = {
            firstname: firstname,
        }

        const url = makeUrl(this.baseURL + '/post-a-bye');
        const payload = toPayload(toSend)

        console.log("--- POST " + url, payload);

        return d3.json(url, payload)
    }

    /**
     * Call MultiModal StoryGenerator to create a text-and-images story according to a given title.
     *
     * @param title
     */
    generateStoryByTitle(title: string): Promise<Story> {
        const toSend = {
            title: title,
        }

        const url = makeUrl(this.baseURL + "/get-a-story", toSend)
        console.log("--- GET " + url);

        return d3.json(url)
    }

    // Options bar.

    /**
     * Call MultiModal StoryGenerator to retreive non-duplicate images according to given extract.
     *
     * @param extract
     */
    retreiveImagesByExtract(extract: string): Promise<Array<string>> {
        const toSend = {
            extract: extract,
        }

        const url = makeUrl(this.baseURL + "/get-image", toSend)
        console.log("--- GET " + url);

        return d3.json(url)
    }


    /**
     * Call MultiModal StoryGenerator to generate text from given extracts (simple generation wihtout re-ranking).
     *
     * @param extracts
     */
    autocompleteTextByAllExtracts(extracts: string): Promise<Array<string>> {
        const toSend = {
            extracts: extracts,
        }

        const url = makeUrl(this.baseURL + "/get-text", toSend)
        console.log("--- GET " + url);

        return d3.json(url)
    }

    // Update according to chosen option/ deletion.

    /**
     * Call MultiModal StoryGenerator to update images according to chosen option.
     *
     * @param img_id     
     * @param to_delete
     */
    updateImages(img_id: string, to_delete: boolean): Promise<string> {
        const toSend = {
            img_id: img_id,
            delete: to_delete,
        }

        const url = makeUrl(this.baseURL + "/update-images", toSend)
        console.log("--- GET " + url);

        return d3.json(url)
    }

    /**
     * Call MultiModal StoryGenerator to update texts according to chosen option.
     *
     * @param extract     
     */
    updateExtracts(extract: string): Promise<string> {
        const toSend = {
            extract: extract,
        }

        const url = makeUrl(this.baseURL + "/update-extracts", toSend)
        console.log("--- GET " + url);

        return d3.json(url)
    }

};
