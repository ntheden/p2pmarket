import React from 'react';
import { Card, Form } from 'react-bootstrap';
import { BsTelegram } from 'react-icons/bs';

import styles from './Footer.module.scss';

export const Footer = () => (
    <Card.Footer className={styles.footer}>
        <BsTelegram />
        <Form.Control
            type="text"
            placeholder="Contact Counterparty..."
            className={styles.addCommentFormInput}
        />
    </Card.Footer>
);
