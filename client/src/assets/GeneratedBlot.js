// Custom generated text blot inspired by https://stackoverflow.com/questions/45421941/can-quill-blockembeds-use-arbitrary-tags
// Block doens't allow for nesting multiple tags, but inlne does
// const Embed = Quill.import('blots/embed');
// class MyCustomTag extends Embed {
//   static create(paramValue) {
//     let node = super.create();
//     node.innerHTML = paramValue;
//     //node.setAttribute('contenteditable', 'false');
//     //node.addEventListener('click', MyCustomTag.onClick);
//     return node;
//   }

//   static value(node) {
//     return node.innerHTML;
//   }
// }

// MyCustomTag.blotName = "my-custom-tag";
// MyCustomTag.className = "my-custom-tag";
// MyCustomTag.tagName = "my-custom-tag";
//in case you need to inject an event from outside
/* MyCustomTag.onClick = function(){
     //do something
 }*/

// Quill.register(MyCustomTag);

//  To insert :
// this.editor.insertEmbed(
// 0, //INDEX_WHERE_YOU_TO_INSERT_THE_CONTENT,
// 'my-custom-tag',//THE NAME OF YOUR CUSTOM TAG
//  '<span>MY CONTENT</SPAN>'// THE CONTENT YOUR TO INSERT
// );

// Change block display in css
// my-custom-tag {
//    display : inline;
// }

// Inline with exsting tag like span
// export class TagBlot extends Inline {
//   static blotName = 'generated';
//   static className = 'generated';
//   static tagName = 'span';

//   static formats(): boolean {
//     return true;
//   }
// }

// export default Embed;

/**
 * Customize generated, Inline with exsting tag like span to be able to nest.
 * Weird behavior with deletions.
 */
//
class Generated extends Embed {
    static create(value) {
        if (!value) return super.create(false);
        let node = super.create(value);
        node.setAttribute("background-color", "#eaf2fb");
        node.innerText = value;
        //node.addEventListener('click', Generated.onClick);
        return node;
    }
    //Returns the value of the node itself for undo operation
    static value(node) {
        return node.innerText;
    }

    // Overriding required for formattable classes.
    static formats(domNode) {
        if (domNode.getAttribute("background-color")) {
            return {
                "background-color": domNode.getAttribute("background-color")
            };
        } else {
            return super.formats(domNode);
        }
    }

    formats() {
        let formats = super.formats();
        formats["generated"] = Generated.formats(this.domNode);
        return formats;
    }
}

Generated.blotName = "generated";
Generated.tagName = "generated";
Generated.className = "generated";

Quill.register(Generated);