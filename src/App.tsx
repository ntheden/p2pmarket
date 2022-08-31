import React, { useState } from 'react';
import styles from './App.module.scss';
import { Col, Row } from 'react-bootstrap';
import { NavbarLayout } from './Main/Navbar/Navbar';
import { OffersBar, FuncProps } from './Main/OffersBar/OffersBar';
import { Feed } from './Main/Feed/Feed';


export const App = () => {
    const [msgId, setMsgId] = useState<number>(0);

    const setId = (id: number) => {
      setMsgId(id);
    };

    return (
        <div className={styles.App}>
            <Row>
                <NavbarLayout />
            </Row>

            <Row className={styles.main}>
                <Col md={{ offset: 2, span: 8 }}>
                    <OffersBar handleMsgIdChange={setId}/>
                    <Feed msgId={msgId}/>
                </Col>
            </Row>
        </div>
    );
};

export default App;
