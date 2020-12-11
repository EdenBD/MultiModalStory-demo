/**
 * Created by Hendrik Strobelt (hendrik.strobelt.com) on 12/3/16.
 * Modified by Ben Hoover on 4/16/2019
 */
import * as d3 from "d3";
import { D3Sel, Sel } from "../etc/Util";
import { EventDetails, SimpleEventHandler } from "../etc/SimpleEventHandler";
import { SVG } from "../etc/SVGplus";

/**
 * Should have VComponentHTML and VComponentSVG
 *
 * Common Properties:
 * - events
 * - eventHandler (V important)
 * - options (Maintains public state. Can expose these with get/set functions with auto update)
 * - _current (Maintains private state)
 * - cssName (synced with corresponding CSS file)
 * - parent (HTML is div containing the base, SVG is SVG element)
 * - base (HTML is div with css_name established)
 * - _data (Data used to create and render the component)
 * - _renderData (Data needed to display. This may not be needed, but is currently used in histogram)
 *
 * Common Methods:
 * - constructor
 * - _render()      Consider replacing with `_updateData()` that updates all data at once
 * - update()       Consider replacing this with `data()` that auto updates data
 * - redraw()
 * - destroy()
 */

abstract class VComponent<DataInterface> {
  // STATIC FIELDS ============================================================

  /**
   * The static property that contains all class related events.
   * Should be overwritten and event strings have to be unique!!
   */

  static events: {} = { noEvent: "VComponent_noEvent" };

  /**
   * Defines the layers in SVG  for bg,main,fg,...
   */
  protected parent: HTMLElement;
  protected options: { [key: string]: any }; // Can be modified from the outside through `updateOptions()`
  protected _current: {};
  protected base: D3Sel; // Represents <g> in SVG and <div> in HTML
  protected layers: {
    main?: D3Sel;
    fg?: D3Sel;
    bg?: D3Sel;
    [key: string]: D3Sel;
  }; // Still useful. Doesn't mean anything for HTML elements
  protected eventHandler: SimpleEventHandler;
  protected visibility: {
    hidden: boolean;
    hideElement?: D3Sel | null;
    [key: string]: any;
  }; // Enables transitions from visible to invisible. Mostly obsolete.
  protected _data: DataInterface;
  protected abstract cssName: string; // Make the same as the corresponding css file

  // CONSTRUCTOR ============================================================

  /**
     * Simple constructor. Subclasses should call @superInit(options) as well.
     * see why here: https://stackoverflow.com/questions/43595943/why-are-derived-class-property-values-not-seen-in-the-base-class-constructor
     *
     * template:
     constructor(d3Parent: D3Sel, eventHandler?: SimpleEventHandler, options: {} = {}) {
        super(d3Parent, eventHandler);
        // -- access to subclass params:
        this.superInit(options);
     }
     *
     * @param {D3Sel} d3parent  D3 selection of parent SVG DOM Element
     * @param {SimpleEventHandler} eventHandler a global event handler object or 'null' for local event handler
     */
  protected constructor(
    parentNode: HTMLElement,
    eventHandler?: SimpleEventHandler
  ) {
    this.parent = parentNode;

    // If not further specified - create a local event handler bound to the bas element
    this.eventHandler = eventHandler || new SimpleEventHandler(this.parent);

    // Object for storing internal states and variables
    this.visibility = { hidden: false };
  }

  /**
   * Should be overwritten to create the static DOM elements. Run manually in the constructor of the instantiated component
   *
   * Axes, paths, ... Everything that needs to be only there once. E.g. adding a layer for tooltip
   *
   * @abstract
   * @return {*} ---
   */
  protected abstract _init();

  /**
   * In order to initialize all static components, this function should be run in the constructor of the class to be instantiated
   */
  protected abstract _superInit();

  // DATA UPDATE & RENDER ============================================================

  /**
   * Complete Redraw
   * Every time data has changed, update is called and
   * triggers wrangling and re-rendering
   * @param {Object} data data object
   * @return {*} ---
   */
  update(data: DataInterface) {
    this._data = data;
    if (this.visibility.hidden) return;
    this._wrangle(data);
    this._render(data);
  }

  /**
   * Create state inside of
   *
   * E.g. determine color scales, redefine axes. By default, does nothing
   *
   * Simplest implementation: `return data;`
   * @param {Object} data data
   * @returns {*} -- data in render format
   * @abstract
   */
  protected _wrangle(data: DataInterface) {}

  /**
   * Is responsible for mapping data to DOM elements
   *
   * @param {Object} renderData pre-processed (wrangled) data
   * @abstract
   * @returns {*} ---
   */
  protected abstract _render(data: DataInterface): void;

  /**
   * Trigger information through the event handler, adding information about the caller to the packet to send
   */
  trigger(eventName: string, packet: {}) {
    packet["caller"] = this;

    const details = <EventDetails>packet;
    this.eventHandler.trigger(eventName, details);
  }

  // UPDATE OPTIONS ============================================================
  /**
   * Updates instance options
   * @param {Object} options only the options that should be updated
   * @param {Boolean} reRender if option change requires a re-rendering (default:false)
   * @returns {*} ---
   */
  updateOptions({ options, reRender = false }) {
    Object.keys(options).forEach(k => (this.options[k] = options[k]));
    if (reRender) this._render(this._data);
  }

  // === CONVENIENCE ====
  redraw() {
    this._render(this._data);
  }

  setHideElement(hE: D3Sel) {
    this.visibility.hideElement = hE;
  }

  hideView() {
    if (!this.visibility.hidden) {
      const hE = this.visibility.hideElement || this.base;
      Sel.hideElement(hE);
      this.visibility.hidden = true;
    }
  }

  unhideView() {
    if (this.visibility.hidden) {
      const hE = this.visibility.hideElement || this.base;
      Sel.unhideElement(hE);
      this.visibility.hidden = false;
    }
  }

  destroy() {
    this.base.remove();
  }

  clear() {
    this.base.html("");
  }
}

export abstract class HTMLComponent<DataInterface> extends VComponent<
  DataInterface
> {
  constructor(
    parent: HTMLElement,
    eventHandler?: SimpleEventHandler,
    options: {} = {}
  ) {
    super(parent, eventHandler);
  }

  protected _superInit(options: {} = {}) {
    Object.keys(options).forEach(key => (this.options[key] = options[key]));
    this.base = d3
      .select(this.parent)
      .append("div")
      .classed(this.cssName, true);
  }
}

export abstract class SVGComponent<DataInterface> extends VComponent<
  DataInterface
> {
  constructor(
    parent: HTMLElement,
    eventHandler?: SimpleEventHandler,
    options: {} = {}
  ) {
    super(parent, eventHandler);
    this._superInit(options);
  }

  protected _superInit(options: {} = {}, defaultLayers = ["bg", "main", "fg"]) {
    Object.keys(options).forEach(key => (this.options[key] = options[key]));

    // Create the base group element
    this.base = d3
      .select(this.parent)
      .append("svg")
      .classed(this.cssName, true);

    this.layers = defaultLayers.reduce((acc, layer) => {
      acc[layer] = SVG.group(this.base, layer);
      return acc;
    }, {});
  }
}
