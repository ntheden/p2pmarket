import axios from "axios";
import React, { useEffect, useState } from 'react';
import { Spinner, Card, Image } from 'react-bootstrap';
import { Header } from './Header/Header';
import { Info } from './Info/Info';
import { Footer } from './Footer/Footer';

import styles from './Feed.module.scss';

export const Feed = ({msgId}: any) => {
    const [msg, setMsg] = useState<any>({});

    useEffect(() => {
        const getMsg = async () => {
          try {
              let response = await axios.get(
                `http://localhost:8001/telegram/@bitcoinp2pmarketplace?msg_id=${msgId}`
              );
              setMsg(response.data);
              console.log("message", response);
          } catch(err) {
              console.log(err);
          }
        };
        getMsg();
    }, [msgId]);

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
              <Info
                username={msg.from_user.username}
              />
              <Footer />
            </Card>
         )}
        </>
    )
};
