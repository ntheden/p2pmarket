import React from 'react';
import { Card, Image } from 'react-bootstrap';
import { Header } from './Header/Header';
import { Info } from './Info/Info';
import { Footer } from './Footer/Footer';

import styles from './Feed.module.scss';

export const Feed = ({msgId}: any) => {
    return (
        <Card className={styles.feed}>
            <Header />

            <Image
                className="w-614"
                src={`http://localhost:8001/telegram/@bitcoinp2pmarket?msg_id=${msgId}&thumb=1`}
            />

            <Info username="Azizoid" />

            <Footer />
        </Card>
    );
};
