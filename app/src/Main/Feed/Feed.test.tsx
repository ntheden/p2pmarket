import React from 'react';
import { render } from '@testing-library/react';
import { Feed } from './Feed';

const msgId = 0;

describe('Renders Feed', () => {
    test('Renders Feed', () => {
        render(<Feed {...msgId}/>);
    });
});
