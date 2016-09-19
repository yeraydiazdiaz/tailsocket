import React from 'react';

import WebSocketConnectionStatus from './WebSocketConnectionStatus.jsx';
import FilePathTextInput from './FilePathTextInput.jsx';

class AsyncLogger extends React.Component {

    constructor(...args) {
        super(...args);
        var protocol = this.props.wssEnabled? 'wss' : 'ws';
        var wsUrl = protocol + '://' + this.props.hostPort + '/websocket/' + this.props.wsName;
        this.state = {
            ws: new WebSocket(wsUrl),
            wsIsConnected: false,
            logging: this.props.logging || 'debug'
        };
        this.onOpen = this.onOpen.bind(this);
        this.onMessage = this.onMessage.bind(this);
        this.onClose = this.onClose.bind(this);
        this.sendMessage = this.sendMessage.bind(this);
        this.onTextAreaChange = this.onTextAreaChange.bind(this);
    }

    log(message) {
        // TODO: actually use logging levels
        if (this.state.logging !== 'none') {
            console.log(this.state.logging.toUpperCase() + ': ' + message);
        }
    }
    componentWillMount() {
        var self = this;
        var ws = self.state.ws;

        ws.onopen = self.onOpen;
        ws.onmessage = self.onMessage;
        ws.onclose = self.onClose;
    }

    componentWillUnmount() {
        this.state.ws.close();
    }

    onMessage(event) {
        this.log(event.data);
        this.setState({
            data: (this.state.data || '') + event.data + '\n'
        });
        this._textarea.scrollTop = this._textarea.scrollHeight;
    }

    onOpen() {
        this.log('WebSocket connected');
        this.setState({
            wsIsConnected: true,
            data: 'Connected! Please enter a path to a log file above.\n'
        });
    }

    onClose() {
        this.log('WebSocket disconnected');
        this.setState({
            wsIsConnected: false,
            data: this.state.data + '\nWebSocket disconnected!'
        });
    }

    sendMessage(message) {
        this.state.ws.send(message);
    }

    onTextAreaChange(event) {
        this.log(event);
    }

    render() {
        var message = this.state.data || 'Hello! Connecting to ' + this.props.hostPort + '...';
        return <div className="asynclogger">
                <WebSocketConnectionStatus connected={this.state.wsIsConnected} />
                <FilePathTextInput
                    sendMessage={this.sendMessage}
                    connected={this.state.wsIsConnected}
                    initialTextValue={this.props.initialTextValue} />
                <textarea readOnly value={ message } onChange={this.onTextAreaChange} ref={(c) => this._textarea = c}></textarea>
            </div>;
    }
}

AsyncLogger.propTypes = {
    hostPort: React.PropTypes.string.isRequired,
    wsName: React.PropTypes.string.isRequired,
    logging: React.PropTypes.string
};

export default AsyncLogger;