import React from 'react';

import { Spinner, Col, Card, Row, Image } from 'react-bootstrap';

import { Username } from 'lib/ui/Username/Username';

import styles from './Profile.module.scss';

export const Profile = ({user}: any) => {
    return(
        <>
        {(user === undefined || Object.keys(user).length === 0) ? (
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
         ) : (
            <Card body={true} bg="light" border="light" className={styles.profile}>
                <Row className="align-items-center">
                    <Col md={{ span: 3 }}>
                        <Image
                            className="w-56"
                            src='generic-user.jpg'
                            roundedCircle={true}
                            thumbnail={true}
                        />
                    </Col>
                    <Col md={{ span: 6 }}>
                        <Username username={user.username} />
                        <Card.Text>{user.first_name} {user.last_name}</Card.Text>
                    </Col>
                    <Col md={{ span: 3 }}>
                        <Card.Link className="profileUsernameLink">Switch</Card.Link>
                    </Col>
                </Row>
            </Card>
        )}
        </>
    )
}
