import axios from "axios";
import React, { useEffect, useState, ReactNode } from 'react';
import { Button, Carousel, ListGroup, Spinner } from 'react-bootstrap';
import Image from 'react-bootstrap/Image';

import { CarouselControls, ControlProps } from './CarouselControls/CarouselControls'
import styles from "./OffersBar.module.scss"
import { apiEndpoint } from '../../App';

export interface FuncProps {
  handleMsgIdChange: (id: number) => void;
};

export const OffersBar = (props: FuncProps): JSX.Element => {
    const [randomOffers, setRandomOffers] = useState<ReactNode[]>([]);
    const [allOfferIds, setAllOfferIds] = useState<number[]>([]);
    const [carouselIndex, setCarouselIndex] = useState<number>(0);
    const [maxIndex, setMaxIndex] = useState<number>(1);

    useEffect(() => {
        const getIds = async () => {
          try {
              let response = await axios.get(`${apiEndpoint}/@bitcoinp2pmarketplace`);
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

    const onNext = () => {
        setCarouselIndex(carouselIndex > 0 ? carouselIndex - 1 : carouselIndex);
    }

    const onPrev = () => {
        setCarouselIndex(carouselIndex < maxIndex ? carouselIndex + 1 : carouselIndex);
    }

    useEffect(() => {
        const randomOfferTempArray = Array.from(
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
                        src={`${apiEndpoint}/@bitcoinp2pmarketplace?msg_id=${randomId}&thumb=1`}
                        roundedCircle={true}
                        thumbnail={true}
                    />
                 )}
            </ListGroup.Item>
        ));
        setRandomOffers(randomOfferTempArray);
        // random initial selection
        carouselSelection(allOfferIds[Math.floor(Math.random() * allOfferIds.length)])
        console.log("randomOffers are:")
        console.log(randomOffers)
    }, [allOfferIds]);

    return (
        <>
        <Carousel data-interval={1000} activeIndex={carouselIndex} indicators={false} controls={false}>
            <Carousel.Item data-bs-interval={1000}>
                <ListGroup horizontal={true}>
                    {randomOffers.slice(0, 6)}
                </ListGroup>
            </Carousel.Item>
            <Carousel.Item data-bs-interval={1000}>
                <ListGroup horizontal={true}>
                    {randomOffers.slice(6, 12)}
                </ListGroup>
            </Carousel.Item>
        </Carousel>
        <CarouselControls onNext={onNext} onPrev={onPrev}/>
        </>
    );
};
