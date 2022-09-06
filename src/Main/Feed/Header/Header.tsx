import React, { useState, useEffect } from 'react';
import { Button, Card, Image, ListGroup, Modal } from 'react-bootstrap';
import { BsThreeDots } from 'react-icons/bs';

import { Username } from 'lib/ui/Username/Username';
import styles from './Header.module.scss';


export const Header = (user: any) => {
    const [postMenuVisibility, setPostMenuVisibility] = useState(false);
    const [photo, setPhoto] = useState("generic-user.jpg");
    const [friendlyName, setFriendlyName] = useState("");

    useEffect(() => {
        let name = ""
        if (user.user.first_name !== null) {
            name = user.user.first_name;
            if (user.user.last_name !== null) {
                name = `${name} ${user.user.last_name}`;
            }
        } else {
            name = user.user.username;
        }
        setFriendlyName(name);
    }, [user]);

    return (
        <Card.Header className={styles.header}>
            <div>
                <Image
                    className={styles.image}
                    src="generic-user.jpg"
                    roundedCircle={true}
                    thumbnail={true}
                />
                <Username username={friendlyName} className={styles.username} />
            </div>
            <Card.Link className={styles.threeDots}>
                <Button
                    onClick={() => setPostMenuVisibility((prev) => !prev)}
                    variant="link">
                    <BsThreeDots role="icon" />
                </Button>
                <Modal
                    show={postMenuVisibility}
                    onHide={() => setPostMenuVisibility(false)}
                    centered={true}>
                    <Modal.Body>
                        <ListGroup variant="flush">
                            {[
                                { title: `Contact ${friendlyName}`, mark: true, href: '#' },
                                {
                                    title: 'Share to...',
                                    mark: false,
                                    href: '#',
                                },
                                { title: 'Copy link', mark: false, href: '#' },
                                { title: 'Embed', mark: false, href: '#' },
                            ].map(({ title, mark, href }, index) => (
                                <ListGroup.Item key={index}>
                                    <a
                                        href={href}
                                        {...(mark && {
                                            className: styles.markedLink,
                                        })}>
                                        {title}
                                    </a>
                                </ListGroup.Item>
                            ))}
                            <ListGroup.Item>
                                <Button
                                    onClick={() => setPostMenuVisibility(false)}
                                    variant="link"
                                    style={{ textDecoration: 'none' }}>
                                    Close
                                </Button>
                            </ListGroup.Item>
                        </ListGroup>
                    </Modal.Body>
                </Modal>
            </Card.Link>
        </Card.Header>
    );
};
