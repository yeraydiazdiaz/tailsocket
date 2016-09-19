var path = require('path');
var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = {
    entry: path.join(__dirname, 'tailsocket/static/src/main.js'),
    output: {
        path: path.join(__dirname, 'tailsocket/static/bin'),
        filename: 'tailsocket.bundle.js',
        publicPath: '/static/bin/'
    },
    module: {
        loaders: [{
            test: /\.jsx?$/,
            exclude: /node_modules/,
            loader: 'babel-loader',
            query: {
                presets: ['es2015', 'react']
            }
        }, {
            test: /\.scss$/,
            loader: ExtractTextPlugin.extract('css!sass')
        }, {
            test:/bootstrap-sass[\/\\]assets[\/\\]javascripts[\/\\]/,
            loader: 'imports?jQuery=jquery'
        }, {
            test: /\.(woff2?|svg)$/,
            loader: 'url?limit=10000'
        }, {
            test: /\.(ttf|eot)$/,
            loader: 'file'
        }]
    },
    plugins: [
        new ExtractTextPlugin('style.css', {
            allChunks: true
        })
    ]
};