import React from 'react';
import { Modal, Card, Form, Button } from 'react-bootstrap';
import { BsTelegram } from 'react-icons/bs';

import styles from './Footer.module.scss';


export const Footer = (user: any) => {

    const handleClick = () => {
        window.open(`https://t.me/${user.user.username}`)
    };

    return (
        <Card.Footer className={styles.footer}>
            <Button variant="outline-success" id={styles.button} onClick={handleClick}>
                Take Offer
            </Button>
        </Card.Footer>
    )
};
