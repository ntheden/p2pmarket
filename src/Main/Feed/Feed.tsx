import axios from "axios";
import React, { useEffect, useState } from 'react';
import { Spinner, Card, Image } from 'react-bootstrap';
import { Header } from './Header/Header';
import { Info } from './Info/Info';
import { Footer } from './Footer/Footer';

import styles from './Feed.module.scss';


export const LoadingUser = {
    first_name: "Loading...",
    last_name: "",
    username: "",
    last_online_date: "",
    status: "UserStatus.OFFLINE",
    thumb_name: "generic-user.jpg",
    media: [],
}

export const Feed = ({data}: any) => {
    const [imageName, setImageName] = useState<string>("no-image.jpg");
    const [user, setUser] = useState<any>(LoadingUser);

    useEffect(() => {
        if (Object.keys(data).length === 0) {
            setUser(LoadingUser);
            return;
        }
        if (data.media.length === 0) {
            setImageName("no-image.jpg");
        } else {
            setImageName(data.media[0].name);
        }
        setUser(data.user);
    }, [data]);

    return (
        <>
        {Object.keys(data).length === 0 ? (
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
         ) : (
            <Card className={styles.feed}>
              <Header user={user}/>
              <Image
                  className="w-614"
                  src={`http://localhost:8001/v1/telegram/media/${imageName}`}
              />
              <Info data={data} />
              <Footer />
            </Card>
         )}
        </>
    )
};
