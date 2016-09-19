import React from 'react';
import {mount, shallow} from 'enzyme';
import jasmineEnzyme from 'jasmine-enzyme';

import FilePathTextInput from '../tailsocket/static/src/components/FilePathTextInput.jsx';

describe('<FilePathTextInput />', () => {
    beforeEach(() => {
        jasmineEnzyme();
    });

    describe('when the "initialTextValue" prop is present', () => {

        it('the text field shows that value', () => {
            const sendMessage = sinon.spy();
            const wrapper = mount(<FilePathTextInput connected={false} sendMessage={sendMessage} initialTextValue={'test'} />);
            expect(wrapper.find('input').props().value).toBe('test');
        });

    });

    describe('when the "connected" prop is false', () => {

        it('the input field is disabled', () => {
            const sendMessage = sinon.spy();
            const wrapper = mount(<FilePathTextInput connected={false} sendMessage={sendMessage} />);
            expect(wrapper.find('fieldset').props().disabled).toBe('disabled');
        });

    });

    describe('when the "connected" prop is true', () => {

        it('the input field is enabled', () => {
            const sendMessage = sinon.spy();
            const wrapper = mount(<FilePathTextInput connected={true} sendMessage={sendMessage} />);
            expect(wrapper.find('fieldset').props().disabled).toBe('');
        });

        describe('when there is no text in the text field', () => {

            it('the input text field and the button are disabled', () => {
                const sendMessage = sinon.spy();
                const wrapper = mount(<FilePathTextInput connected={true} sendMessage={sendMessage} />);
                expect(wrapper.find('button').props().disabled).toBe('disabled');
            });

            it('pressing the Enter key does not trigger a sendMessage', () => {
                const sendMessage = sinon.spy();
                const wrapper = mount(<FilePathTextInput connected={true} sendMessage={sendMessage} />);
                const input = wrapper.find('input');
                input.simulate('keyUp', {which: 13});
                expect(sendMessage.calledOnce).toBe(false);
            });

            it('pressing any key other than Enter changes the value state', () => {
                const sendMessage = sinon.spy();
                const wrapper = mount(<FilePathTextInput connected={true} sendMessage={sendMessage} />);
                const input = wrapper.find('input');
                input.node.value = 'a';  // Simulating key presses does not update the node's value
                input.simulate('change');
                expect(wrapper.state('value')).toEqual('a')
            });

        });

        describe('when there is text in the text field', () => {

            it('pressing Enter the sendMessage is called with the contents of the text input', () => {
                const sendMessage = sinon.spy();
                const wrapper = mount(<FilePathTextInput connected={true} sendMessage={sendMessage} />);
                const input = wrapper.find('input');
                input.node.value = '/path/to/file';
                input.simulate('keyUp', {which: 13});
                expect(sendMessage.calledOnce).toBe(true);
                expect(sendMessage.calledWith(input.node.value)).toEqual(true);
            });

            it('removing the text disables the button', () => {
                const sendMessage = sinon.spy();
                const wrapper = mount(<FilePathTextInput connected={true} sendMessage={sendMessage} />);
                const button = wrapper.find('button');
                const input = wrapper.find('input');
                input.node.value = 'e';
                input.simulate('change');  // needed to update the disabled state
                expect(wrapper.find('fieldset').props().disabled).toBe('');
                expect(button.props().disabled).toBe('');
                expect(wrapper.state('value')).toEqual('e')

                input.node.value = '';
                input.simulate('change');

                expect(wrapper.state('value')).toEqual('')
                expect(button.props().disabled).toBe('disabled');
            });

            it('when pressing the button the sendMessage is called with the contents of the text input', () => {
                const sendMessage = sinon.spy();
                const wrapper = mount(<FilePathTextInput connected={true} sendMessage={sendMessage} />);
                const input = wrapper.find('input');
                const button = wrapper.find('button');

                const path = '/path/to/file'
                input.node.value = path;
                input.simulate('change');  // needed to update the disabled state

                expect(wrapper.find('fieldset').props().disabled).toBe('');
                expect(button.props().disabled).toBe('');

                button.simulate('click');
                expect(sendMessage.calledOnce).toBe(true);
                expect(sendMessage.calledWith(path)).toEqual(true);
            });

        });

    });

});
