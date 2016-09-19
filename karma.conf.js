var path = require('path');
var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = function(config) {
  config.set({
    basePath: '',
    frameworks: ['jasmine', 'sinon'],
    files: [
      'tests/**/*.jsx'
    ],

    preprocessors: {
      // add webpack as preprocessor
      'tests/**/*.jsx': ['webpack', 'sourcemap']
    },

    //kind of a copy of your webpack config
    webpack: {
      //just do inline source maps instead of the default
      devtool: 'inline-source-map',
      externals: {
        'react/addons': true,
        'react/lib/ExecutionEnvironment': true,
        'react/lib/ReactContext': true
      },
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
          }, {
            test: /\.json$/,
            loader: 'json-loader'
          }]
      },
      plugins: [
          new ExtractTextPlugin('style.css', {
              allChunks: true
          })
      ]
    },

    webpackServer: {
      //please don't spam the console when running in karma!
      noInfo: true
    },

    plugins: [
      'karma-webpack',
      'karma-jasmine',
      'karma-sinon',
      'karma-sourcemap-loader',
      'karma-chrome-launcher',
      'karma-phantomjs-launcher'
    ],

    babelPreprocessor: {
      options: {
        presets: ['airbnb']
      }
    },
    reporters: ['progress'],
    port: 9876,
    colors: true,
    logLevel: config.LOG_DEBUG,
    autoWatch: true,
    browsers: ['PhantomJS'],
    singleRun: false,
    client: {
      captureConsole: true
    }
  })
};
