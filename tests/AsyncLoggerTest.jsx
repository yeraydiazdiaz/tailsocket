import React from 'react';
import {mount, shallow} from 'enzyme';
import jasmineEnzyme from 'jasmine-enzyme';

import AsyncLogger from '../tailsocket/static/src/components/AsyncLogger.jsx';

describe('<AsyncLogger />', () => {
    beforeEach(() => {
        jasmineEnzyme();
    });

    describe('when websocket is disconnected', () => {

        it('the status and file path input have a connected prop of false', () => {
            const wrapper = mount(<AsyncLogger host_port='localhost:8888' wsName='name' />);
            expect(wrapper.childAt(0).props().connected).toBe(false);
            expect(wrapper.childAt(1).props().connected).toBe(false);
        });

        it('and the websocket connects the status and file path input have a connected prop of true', () => {
            const wrapper = mount(<AsyncLogger host_port='localhost:8888' wsName='name' />);
            wrapper.setState({wsIsConnected: true})
            expect(wrapper.childAt(0).props().connected).toBe(true);
            expect(wrapper.childAt(1).props().connected).toBe(true);
        });

    });

    describe('when websocket is connected', () => {

        describe('and sendMessage is called with a path', () => {

            it('a message is sent with the content of sendMessage', () => {
                const wrapper = mount(<AsyncLogger host_port='localhost:8888' wsName='name' />);
                let ws = wrapper.state('ws')
                ws.send = sinon.spy()
                wrapper.setState({wsIsConnected: true, ws: ws})
                wrapper.instance().sendMessage('/path/to/file')
                expect(ws.send.calledWith('/path/to/file')).toBe(true);
            });

        });

        describe('and a message is recieved from the websocket', () => {

            it('the textarea should display the message', () => {
                const wrapper = mount(<AsyncLogger host_port='localhost:8888' wsName='name' />);
                wrapper.setState({wsIsConnected: true});
                const logline = 'logline';
                wrapper.instance().onMessage({data: logline});
                expect(wrapper.state('data')).toContain(logline);
                expect(wrapper.find('textarea').props().value).toContain(logline);
            });

            it('the textarea should scroll to the bottom', () => {
                const wrapper = mount(<AsyncLogger host_port='localhost:8888' wsName='name' />);
                const textarea = wrapper.find('textarea');
                wrapper.setState({wsIsConnected: true});
                const logline = 'logline';
                wrapper.instance().onMessage({data: logline});
                expect(textarea.props().scrollTop).toEqual(textarea.props().scrollHeight);
            });

        });

        describe('and the websocket closes', () => {

            it('the status and file path input are passed a connected prop of false', () => {
                const wrapper = mount(<AsyncLogger host_port='localhost:8888' wsName='name' />);
                wrapper.setState({wsIsConnected: true})
                wrapper.instance().onClose();
                expect(wrapper.state('wsIsConnected')).toBe(false);
                expect(wrapper.childAt(0).props().connected).toBe(false);
                expect(wrapper.childAt(1).props().connected).toBe(false);
            });

        });

        describe('and the component will unmount', () => {

            it('the websocket closes', () => {
                const wrapper = mount(<AsyncLogger host_port='localhost:8888' wsName='name' />);
                wrapper.setState({wsIsConnected: true})
                let ws = wrapper.state('ws')
                ws.close = sinon.spy()
                wrapper.unmount();
                expect(ws.close.calledOnce).toBe(true);
            });

        });

    });

});
