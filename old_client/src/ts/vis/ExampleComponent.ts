import * as d3 from 'd3'
import { D3Sel } from '../etc/Util'
import { HTMLComponent, SVGComponent } from './VComponent'
import { SimpleEventHandler } from '../etc/SimpleEventHandler'

type DI = string[]

export class HTMLList extends HTMLComponent<DI>{
    cssName = "HTMLList"

    constructor(parent:HTMLElement, eventHandler?:SimpleEventHandler, options={}) {
        super(parent, eventHandler, options)
        this._superInit(options);
        this._init()
    }

    static events = {
        mouseOver: "WordList_MouseOver",
        mouseOut: "WordList_MouseOut",
        click: "WordList_Click",
        dblClick: "WordList_DblClick",
    }

    _init() { 
        const mainLayer = this.base.append('div').classed('main-layer', true)
    }

    _render(data: DI) {
        const self = this
        const wordBoxes = self.base.selectAll('.word-box')
            .data(data)
            .join('div')
            .classed('word-box', true)
            .text(d => d)
            .on('click', d => {
                self.trigger(HTMLList.events.click, {name: d})
            })
            .on('mouseover', d => {
                self.trigger(HTMLList.events.mouseOver, {name: d})
            })
    }
}

export class SVGList extends SVGComponent<DI>{
    cssName = "WordList"

    constructor(parent:HTMLElement, eventHandler?:SimpleEventHandler, options={}) {
        super(parent, eventHandler, options)
        this._superInit(options);
        this._init()
    }

    static events = {
        mouseOver: "WordList_MouseOver",
        mouseOut: "WordList_MouseOut",
        click: "WordList_Click",
        dblClick: "WordList_DblClick",
    }

    _init() { } 

    _render(data: DI) {}
}