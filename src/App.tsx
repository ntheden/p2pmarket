import axios from "axios";
import React, { useState, useEffect } from 'react';
import styles from './App.module.scss';
import { Col, Row } from 'react-bootstrap';
import { NavbarLayout } from './Main/Navbar/Navbar';
import { OffersBar, FuncProps } from './Main/OffersBar/OffersBar';
import { Profile } from './Main/Profile/Profile';
import { Feed, LoadingUser } from './Main/Feed/Feed';


export const App = () => {
    const [msgId, setMsgId] = useState<number>(0);
    const [data, setData] = useState<any>({});
    const [user, setUser] = useState<any>(LoadingUser);

    useEffect(() => {
        const getMsg = async () => {
          if (msgId === undefined) {
            return;
          }
          try {
              let response = await axios.get(
                `http://localhost:8001/v1/telegram/@bitcoinp2pmarketplace?msg_id=${msgId}`
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
        <div className={styles.App}>
            <Row>
                <NavbarLayout />
            </Row>

            <Row className={styles.main}>
                <Col md={{ offset: 2, span: 6 }}>
                    <OffersBar handleMsgIdChange={setId}/>
                    <Feed data={data}/>
                </Col>
                <Col md={{ span: 3 }}>
                    <Profile user={user} />
                </Col>
            </Row>
        </div>
    );
};

export default App;
