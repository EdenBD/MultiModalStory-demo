/**
 * Created by hen on 5/15/17.
 * Modified by hoo on 4/16/19.
 */

/**
 * Ensure the class calling the event emits itself in the 'caller' key of details
 */
export interface EventDetails {
    caller: any
}

export class SimpleEventHandler {

    element: Element;
    eventListeners: object[];

    constructor(element: Element) {
        this.element = element;
        this.eventListeners = []
    }

    bind(eventNames: string, eventFunction: Function) {
        for (const eventName of eventNames.split(' ')) {
            this.eventListeners.push({eventName, eventFunction});
            const eventFunctionWrap = e => eventFunction(e.detail, e);
            this.element.addEventListener(eventName, eventFunctionWrap, false);
        }
    }

    getListeners() {
        return this.eventListeners;
    }

    trigger(eventName: string, detail: {caller: any}) {
        this.element.dispatchEvent(new CustomEvent(eventName, {detail}));
    }
}