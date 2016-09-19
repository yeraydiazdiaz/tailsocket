import React from 'react';

class FilePathTextInput extends React.Component {

    constructor(...args) {
        super(...args);
        this.state = {
            value: this.props.initialTextValue
        };
        this.onButtonClick = this.onButtonClick.bind(this);
        this.onKeyUp = this.onKeyUp.bind(this);
        this.onChange = this.onChange.bind(this);
    }

    onButtonClick() {
        const filePath = this.refs.textinput.value;
        if (filePath) {
            this.props.sendMessage(filePath);
        }
    }

    onKeyUp(e) {
        if (e.which === 13) {
            this.onButtonClick();
        }
    }

    onChange(e) {
        this.setState({'value': e.currentTarget.value})
    }

    render() {
        return <fieldset className="file-path-text-input" disabled={this.props.connected? '' : 'disabled'}>
                <label>Path to file:
                <input id="message-input-text"
                       ref="textinput"
                       type="text"
                       value={this.state.value}
                       onChange={this.onChange}
                       onKeyUp={this.onKeyUp}
                       />
                <button className="btn btn-primary" id="send-message-btn"
                    disabled={this.state.value? '' : 'disabled'}
                    onClick={this.onButtonClick} >Tail it!</button>
                </label>
                <ul>
                    <li>Paths can be absolute or relative to the app's working directory</li>
                    <li>Files must be readable by the owner of the Tailsocket process</li>
                </ul>
            </fieldset>
    }
}

FilePathTextInput.propTypes = {
    sendMessage: React.PropTypes.func.isRequired
};

export default FilePathTextInput;