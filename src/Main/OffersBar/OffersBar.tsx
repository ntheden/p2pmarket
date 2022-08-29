import axios from "axios";
import React, { useEffect, useState, ReactNode } from 'react';
import { Carousel, ListGroup, Spinner } from 'react-bootstrap';
import Image from 'react-bootstrap/Image';

export const OffersBar = (): JSX.Element => {
    const [randomOffers, setRandomOffers] = useState<ReactNode[]>();
    const [allOfferIds, setAllOfferIds] = useState<number[]>([]);

    useEffect(() => {
        const getIds = async () => {
          try {
              let response = await axios.get(
                `https://localhost:8001/tg/@bitcoinp2pmarketplace`
              );
              setAllOfferIds(response.data);
              console.log(allOfferIds);
          } catch(err) {
              console.log(err);
          }
        };
    }, []);

    useEffect(() => {
        const randomOfferisTemp = Array.from(
            { length: 12 },
            () => allOfferIds[Math.floor(Math.random() * allOfferIds.length)],
        ).map((randomNumber, index) => (
            <ListGroup.Item key={index}>
                <Image
                    className="w-80"
                    src={`http://localhost:8001/tg/@bitcoinp2pmarket?msg_id=${randomNumber}&photo=1`}
                    roundedCircle={true}
                    thumbnail={true}
                />
            </ListGroup.Item>
        ));

        setRandomOffers(randomOfferisTemp);
    }, []);

    if (!randomOffers)
        return (
            <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
            </Spinner>
        );

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
