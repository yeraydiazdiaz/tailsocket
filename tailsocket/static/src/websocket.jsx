import React from 'react';
import ReactDOM from 'react-dom';
const classNames = require('classnames');
const uuid = require('node-uuid');

require('./styles/main.scss');
require('bootstrap-loader');

import AsyncLogger from './components/AsyncLogger.jsx';

class TailSocketApp extends React.Component {

    constructor(...args) {
        super(...args);
        const outputElement = document.getElementById('output')
        const hostPortData = outputElement.getAttribute('data-host-port');
        const initialTextValue = outputElement.getAttribute('data-initial-text-value');
        const wssEnabled = document.location.href.startsWith('https://');
        const hostPort = hostPortData ? hostPortData : document.location.host;
        const id = uuid.v4();
        const loggers = [
            <AsyncLogger
                hostPort={hostPort}
                wssEnabled={wssEnabled}
                wsName={id}
                initialTextValue={initialTextValue}
                key={id} />
        ];
        this.state = {
            loggers: loggers
        };
    }

    render() {
        return <div>{this.state.loggers}</div>;
    }
}

ReactDOM.render(<TailSocketApp/>, document.getElementById('output'));