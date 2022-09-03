import axios from "axios";
import React, { useEffect, useState, ReactNode } from 'react';
import { Carousel, ListGroup, Spinner } from 'react-bootstrap';
import Image from 'react-bootstrap/Image';

import styles from "./OffersBar.module.scss"

export interface FuncProps {
  handleMsgIdChange: (id: number) => void;
};

export const OffersBar = (props: FuncProps): JSX.Element => {
    const [randomOffers, setRandomOffers] = useState<ReactNode[]>([]);
    const [allOfferIds, setAllOfferIds] = useState<number[]>([]);

    useEffect(() => {
        const getIds = async () => {
          try {
              let response = await axios.get(
                `http://localhost:8001/v1/telegram/@bitcoinp2pmarketplace`
              );
              setAllOfferIds(response.data);
              console.log("allOfferIds are:");
              console.log(allOfferIds);
          } catch(err) {
              console.log(err);
          }
        };
        getIds();
    }, []);

    const carouselSelection = (msgId: number) => {
        props.handleMsgIdChange(msgId);
    }

    useEffect(() => {
        const randomOfferisTemp = Array.from(
            { length: 12 },
            () => allOfferIds[Math.floor(Math.random() * allOfferIds.length)],
        ).map((randomId, index) => (
            <ListGroup.Item key={index} onClick={() => carouselSelection(randomId)}>
                {randomId === undefined ? (
                    <Spinner animation="border" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </Spinner>
                 ) : (
                    <Image
                        className="w-80"
                        src={`http://localhost:8001/v1/telegram/@bitcoinp2pmarket?msg_id=${randomId}&thumb=1`}
                        roundedCircle={true}
                        thumbnail={true}
                    />
                 )}
            </ListGroup.Item>
        ));
        setRandomOffers(randomOfferisTemp);
        console.log("randomOffers are:")
        console.log(randomOffers)
    }, [allOfferIds]);

    return (
        <Carousel>
            <Carousel.Item>
                <ListGroup horizontal={true}>
                    {randomOffers.slice(0, 6)}
                </ListGroup>
            </Carousel.Item>
            <Carousel.Item>
                <ListGroup horizontal={true}>
                    {randomOffers.slice(6, 12)}
                </ListGroup>
            </Carousel.Item>
        </Carousel>
    );
};
