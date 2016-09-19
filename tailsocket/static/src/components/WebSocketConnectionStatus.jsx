import React from 'react';
var classNames = require('classnames');

require('../styles/main.scss');
require('bootstrap-loader');

class WebSocketConnectionStatus extends React.Component {
    constructor(...args) {
        super(...args);
        this.state = {
            connected: false
        };
    }

    render() {
        var statusClass = classNames('connection-status', {
            'connected': this.props.connected,
            'disconnected': !this.props.connected
        });
        var connectionClass = classNames('glyphicon', {
            'glyphicon-ok': this.props.connected,
            'glyphicon-remove': !this.props.connected,
        });
        return <p className={ statusClass } title={`Websocket ${this.props.connected? 'connected':'disconnected'}`}>
            <span className={ connectionClass }></span>
        </p>;
    }
}

export default WebSocketConnectionStatus;