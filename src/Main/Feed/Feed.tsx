import axios from "axios";
import React, { useEffect, useState } from 'react';
import { Spinner, Card, Image } from 'react-bootstrap';
import { Header } from './Header/Header';
import { Info } from './Info/Info';
import { Footer } from './Footer/Footer';

import styles from './Feed.module.scss';

export const Feed = ({msg}: any) => {
    return (
        <>
        {Object.keys(msg).length === 0 ? (
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
         ) : (
            <Card className={styles.feed}>
              <Header />
              <Image
                  className="w-614"
                  src={`http://localhost:8001/telegram/@bitcoinp2pmarket?msg_id=${msg.id}&photo=1`}
              />
              <Info msg={msg} />
              <Footer />
            </Card>
         )}
        </>
    )
};
