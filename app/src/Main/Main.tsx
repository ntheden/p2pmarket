import axios from "axios";
import React, { useState, useEffect } from 'react';
import styles from './Main.module.scss';
import { Col, Row } from 'react-bootstrap';
import { NavbarLayout } from './Navbar/Navbar';
import { OffersBar } from './OffersBar/OffersBar';
import { Feed, LoadingUser } from './Feed/Feed';


const getEndpoint = () => {
    let endPoint = process.env.REACT_APP_API_ENDPOINT;
    if (endPoint === undefined) {
        endPoint = "";
    }
    return endPoint;
};
export const apiEndpoint =  `${getEndpoint()}/v1/telegram`;


export const Main = () => {
    const [msgId, setMsgId] = useState<number>(0);
    const [data, setData] = useState<any>({});
    const [user, setUser] = useState<any>(LoadingUser);

    useEffect(() => {
        const getMsg = async () => {
          if (msgId === undefined || msgId === 0) {
            return;
          }
          try {
              let response = await axios.get(
                     `${apiEndpoint}/@bitcoinp2pmarketplace?msg_id=${msgId}`
              );
              setData(response.data);
              setUser(response.data.user);
              console.log("message", response);
          } catch(err) {
              console.log(err);
          }
        };
        getMsg();
    }, [msgId]);


    const setId = (id: number) => {
      console.log("msgId", id);      
      setMsgId(id);
    };

    return (
        <div className={styles.Main}>
            <Row>
                <NavbarLayout />
            </Row>

            <Row className={styles.main}>
                <Col md={{ offset: 2, span: 8 }}>
                    <OffersBar handleMsgIdChange={setId}/>
                    <Feed data={data}/>
                </Col>
            </Row>
        </div>
    );
}
