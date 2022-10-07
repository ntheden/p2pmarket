import axios from "axios";
import React, { useEffect, useState, ReactNode } from 'react';
import { Button, Carousel, ListGroup, Spinner } from 'react-bootstrap';
import Image from 'react-bootstrap/Image';

import { CarouselControls, ControlProps } from './CarouselControls/CarouselControls'
import styles from "./OffersBar.module.scss"
import { apiEndpoint } from '../Main';

export interface FuncProps {
  handleMsgIdChange: (id: number) => void;
};

export const OffersBar = (props: FuncProps): JSX.Element => {
    const [carouselItems, setCarouselItems] = useState<ReactNode[]>([]);
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

    const filter = (ar: Array<number>) => {
        // TODO: filter out stuff that doesn't match, for instance:
        // 1. has picture
        // 2. has word on the user's banned list. There will
        //    be a default short list of banned words that the user
        //    can modify
        const filters = localStorage.getItem('carousel.filters');
        console.log("filters", filters);
        return ar;
    }

    const shuffle = (o: Array<number>) => {
      for (var j, x, i = o.length;
           i;
           j = Math.floor(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x
      );
      return o;
    }

    const arrange = (ar: Array<number>) => {
        enum eArrangement {
            Shuffle = "Shuffle",
            Newest = "Newest",
            Oldest = "Oldest",
        }
        let arrangement = localStorage.getItem('carousel.arrangement');
        if (arrangement === null) {
            localStorage.setItem('carousel.arrangement', eArrangement.Shuffle);
            arrangement = eArrangement.Newest;
        }
        console.log("arrangement", arrangement);
        switch(arrangement) {
            case eArrangement.Shuffle:
                return shuffle(ar);
            case eArrangement.Newest:
                return ar.sort((first: number, second: number) => {
                    return (first > second ? -1 : 1)
                })
            case eArrangement.Oldest:
                return ar.sort((first: number, second: number) => {
                    return (first > second ? 1 : -1)
                })
        }
        // default
        return shuffle(ar);
    }

    const chunks = (ar: Array<number>) => {
        let count = ar.length / 6;
        let ar1 = [];
        console.log(`Looking at ${count} swipes`);
        setMaxIndex(count);
        for (let i=0; i<count; i++) {
            ar1.push(ar.splice(0, 6).map((item, index) => (
              <ListGroup.Item key={(i*6)+index} onClick={() => carouselSelection(item)}>
                {item === undefined ? (
                    <Spinner animation="border" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </Spinner>
                 ) : (
                    <Image
                        className="w-80"
                        src={`${apiEndpoint}/@bitcoinp2pmarketplace?msg_id=${item}&thumb=1`}
                        roundedCircle={true}
                        thumbnail={true}
                    />
                 )}
              </ListGroup.Item>
            )));
        } 
        return ar1;
    }

    const listChunks = (chunks: Array<any>) => {
        return chunks.map((chunk) => (
            <Carousel.Item data-bs-interval={1000}>
                <ListGroup horizontal={true}>
                    {chunk}
                </ListGroup>
            </Carousel.Item>
        ));
    }

    useEffect(() => {
        const msgIds = filter(arrange(allOfferIds));
        carouselSelection(msgIds[0]);
        setCarouselItems(listChunks(chunks(msgIds)));
    }, [allOfferIds]);

    return (
        <>
        <Carousel data-interval={1000} activeIndex={carouselIndex} indicators={false} controls={false}>
        {carouselItems}
        </Carousel>
        <CarouselControls onNext={onNext} onPrev={onPrev}/>
        </>
    );
};
