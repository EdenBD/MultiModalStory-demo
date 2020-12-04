import {main} from './ts/main'

import "!file-loader?name=index.html!./index.html";
import "./css/main.scss"


window.onload = () => {
    main()
    console.log("Done loading window");
}