import React from 'react';
import {mount, shallow} from 'enzyme';
import jasmineEnzyme from 'jasmine-enzyme';

import WebSocketConnectionStatus from '../tailsocket/static/src/components/WebSocketConnectionStatus.jsx';

describe('<WebSocketConnectionStatus />', () => {
    beforeEach(() => {
        jasmineEnzyme();
    });

    describe('when "connected" prop is false', () => {

        it('shows red cross icon', () => {
            const wrapper = shallow(<WebSocketConnectionStatus connected={false} />);
            expect(wrapper.find('span').hasClass('glyphicon-remove')).toBe(true);
            expect(wrapper.find('span').hasClass('glyphicon-ok')).toBe(false);
        });

    });

    describe('when "connected" prop is true', () => {

        it('shows green tick mark icon', () => {
            const wrapper = shallow(<WebSocketConnectionStatus connected={true} />);
            expect(wrapper.find('span').hasClass('glyphicon-ok')).toBe(true);
            expect(wrapper.find('span').hasClass('glyphicon-remove')).toBe(false);
        });

    });

});
