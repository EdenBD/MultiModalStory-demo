const merge = require('webpack-merge');
const common = require('./webpack.common.js');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const HtmlWebpackExternalsPlugin = require('html-webpack-externals-plugin')

module.exports = merge(common, {
    mode: 'production',
    plugins: [
        new HtmlWebpackPlugin({
            template: "src/index.html",
            inject: "body"
        }),
        new HtmlWebpackExternalsPlugin({
            externals: [
                {
                    module: 'd3',
                    entry: "https://unpkg.com/d3@5.15.0/dist/d3.min.js",
                    global: 'd3'
                },
                {
                    module: 'lodash',
                    entry: "https://unpkg.com/lodash@1.0.2/dist/lodash.min.js",
                    global: 'lodash'
                },
            ]
        }),
    ]
});