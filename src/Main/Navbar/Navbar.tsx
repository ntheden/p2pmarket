import React, { useEffect, useState } from "react";
import { Sling as Hamburger } from 'hamburger-react'
import {
    BsSearch,
    BsHouseDoor,
    BsMessenger,
    BsPlusSquare,
    BsCompass,
    BsHeart,
    BsFillEmojiSmileUpsideDownFill,
} from 'react-icons/bs';
import styles from './Navbar.module.scss';

import {
    Col,
    Container,
    FormControl,
    InputGroup,
    Nav,
    Navbar,
    Row,
} from 'react-bootstrap';

export const NavbarLayout = () => {
    const [burgerIsOpen, setBurgerIsOpen] = useState<boolean>(false);

    useEffect(() => {
        if (burgerIsOpen) {
            console.log("Burger is open");
        } else {
            console.log("Burger is closed");
        }
    }, [burgerIsOpen]);

    return (
        <Navbar className={styles.navbar}>
            <Col md={{ offset: 2, span: 9 }}>
                <Container>
                    <Row>
                        <Col md={{ span: 3 }}>
                            <Navbar.Brand href="#home" className={styles.brand}>
                                @bitcoinp2pmarketplace
                            </Navbar.Brand>
                        </Col>
                        <Col md={{ span: 5 }} className={styles.searchBar}>
                            <InputGroup>
                                <InputGroup.Text className={styles.searchInput}>
                                    <BsSearch />
                                </InputGroup.Text>
                                <FormControl
                                    placeholder="Search"
                                    aria-label="Search"
                                />
                            </InputGroup>
                        </Col>
                        <Col md={{ offset: 2, span: 2 }}>
                            <Hamburger toggled={burgerIsOpen} toggle={setBurgerIsOpen}/>
                        </Col>
                    </Row>
                </Container>
            </Col>
        </Navbar>
    )
};
