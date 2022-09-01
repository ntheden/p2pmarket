import React, { useState } from 'react';
import styles from './App.module.scss';
import { Col, Row } from 'react-bootstrap';
import { NavbarLayout } from './Main/Navbar/Navbar';
import { OffersBar, FuncProps } from './Main/OffersBar/OffersBar';
import { Profile } from './Main/Profile/Profile';
import { Feed } from './Main/Feed/Feed';


export const App = () => {
    const [msgId, setMsgId] = useState<number>(0);
    const [me] = useState({
        username: 'azizoid',
        fullName: 'Aziz Shahhuseynov',
        image: 'https://picsum.photos/56',
    });

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
                    <Feed msgId={msgId}/>
                </Col>
                <Col md={{ span: 3 }}>
                    <Profile {...me} />
                </Col>
            </Row>
        </div>
    );
};

export default App;
