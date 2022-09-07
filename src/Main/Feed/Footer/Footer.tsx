import React from 'react';
import { Card, Form, Button } from 'react-bootstrap';
import { BsTelegram } from 'react-icons/bs';

import styles from './Footer.module.scss';

export const Footer = () => (
    <Card.Footer className={styles.footer}>
        <Button variant="outline-success" id={styles.button}>
            Take Offer
        </Button>
    </Card.Footer>
);
