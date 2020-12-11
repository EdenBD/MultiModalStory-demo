import { URLHandler } from "./etc/URLHandler";
// import * as _ from "lodash"
// import * as tp from './types'
// import * as tf from "@tensorflow/tfjs"

interface URLParameters {
  sentence: string;
}

interface StateConf {}

export class State {
  private _url: Partial<URLParameters> = {};
  private _conf: Partial<StateConf> = {};

  constructor() {
    this.fromURL();
    this.toURL(false);
  }

  /**
   * Reads app state from the URL, setting default values as necessary
   */
  fromURL() {
    const params = URLHandler.parameters;

    this._url = {
      sentence: params["sentence"] || ""
    };
  }

  toURL(updateHistory = false) {
    URLHandler.updateUrl(this._url, updateHistory);
  }

  sentence(): string;
  sentence(val: string): this;
  sentence(val?) {
    if (val == null) return this._url.sentence;
    this._url.sentence = val;
    this.toURL();
    return this;
  }
}
