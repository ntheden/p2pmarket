import axios from "axios";
import React, { ReactNode, useEffect, useState } from 'react';
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
    const [user, setUser] = useState<any>(LoadingUser);
    const [image, setImage] = useState<ReactNode>(<></>);

    useEffect(() => {
        if (Object.keys(data).length === 0) {
            setUser(LoadingUser);
            return;
        }
        if (data.media.length === 0) {
            setImage(
                <Image
                  id={styles.image}
                  className="w-25"
                  src={`http://localhost:8001/v1/telegram/media/no-image.jpg`}
                />
            );
        } else {
            setImage(
                <Image
                  className="w-100"
                  src={`http://localhost:8001/v1/telegram/media/${data.media[0].name}`}
                />
            );
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
              <Header user={user} />
              {image}
              <Info data={data} />
              <Footer user={user}/>
            </Card>
         )}
        </>
    )
};
