const merge = require('webpack-merge');
const common = require('./webpack.common.js');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = merge(common, {
    mode: 'development',
    devtool: 'inline-source-map',
    devServer: {
        port: 8090,
        proxy: {
            '/api/*': {
                target: 'http://localhost:8080',
                secure: false,
                ws: true
            }
        }
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: "src/index.html",
            inject: "body"
        }),]
});