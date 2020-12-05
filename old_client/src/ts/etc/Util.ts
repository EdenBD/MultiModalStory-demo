import * as d3 from "d3";
import { BaseType } from "d3";

/**
 * Created by hen on 5/15/17.
 * Modifyed by hoo on 4/16/19.
 */
let the_unique_id_counter = 0;

export class Util {
    static simpleUId({ prefix = '' }): string {
        the_unique_id_counter += 1;

        return prefix + the_unique_id_counter;
    }
}

export type D3Sel = d3.Selection<any, any, any, any>

/**
 * Selection utility functions should be static methods in the below class
 */
export class Sel {
    static setSelVisible = (x: D3Sel) => x.attr("visibility", "visible")
    static setSelHidden = (x: D3Sel) => x.attr("visibility", "hidden")
    static setVisible = (x: string) => Sel.setSelVisible(d3.selectAll(x))
    static setHidden = (x: string) => Sel.setSelHidden(d3.selectAll(x))
    static hideElement = (hE: D3Sel) => hE.transition()
                                            .style('opacity', 0)
                                            .style('pointer-events', 'none')
                                            .style('display', 'none')
    static unhideElement = (hE: D3Sel) => hE.transition()
                                            .style('opacity', 1)
                                            .style('pointer-events', null)
                                            .style('display', null)
}

export interface LooseObject {
    [key: string]: any
}

export type d3S<T extends BaseType, U = any> = d3.Selection<T, U, any, any>

/** 
 * From https://stackoverflow.com/questions/33855641/copy-output-of-a-javascript-variable-to-the-clipboard
 * 
 * Copy specified `text` to clipboard
 */
export function copyToClipboard(text:string) {
    var dummy = document.createElement("textarea");
    // to avoid breaking orgain page when copying more words
    // cant copy when adding below this code
    document.body.appendChild(dummy);
    //Be careful if you use textarea. setAttribute('value', value), which works with "input" does not work with "textarea". – Eduard
    d3.select(dummy).attr('value', text);
    dummy.value = text
    dummy.select();
    console.log(dummy);
    document.execCommand("copy");
    document.body.removeChild(dummy);
}