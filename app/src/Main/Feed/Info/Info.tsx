import React, { useEffect, useState, ReactNode } from 'react';
import { Spinner, Card, Badge, ListGroup } from 'react-bootstrap';
import { BsHeart, BsChatRight, BsTelegram, BsBookmark } from 'react-icons/bs';
//import { DateTime } from "luxon";

import { Username } from 'lib/ui/Username/Username';
import styles from './Info.module.scss';
import { Reactions } from './Reactions/Reactions'


export const Info = ({data}: any) => {
    const [ago, setAgo] = useState<string>("Long time ago...");
    const [hashtags, setHashtags] = useState<ReactNode[]>([]);

    useEffect(() => {
        if (data === undefined || Object.keys(data).length === 0) {
            return;
        }
        console.log(data.message.caption);
    }, [data]);

    const computeAgo = (date: string) => {
        if (date === null || date == 'uknown post date') {
            return 'unknown post date';
        }
        const sec: number = (Number(new Date()) - Number(new Date(date))) / 1000;
        const minutes: number = (sec / 60) | 0;
        const hours: number = (sec / 3600) | 0;
        const days: number = (sec / 86400) | 0;
        const months: number = (sec / 2592000) | 0;
        const years: number = (sec / 31536000) | 0;
        console.log("date", data.message.date);
        // rough estimate
        return years > 0 ? `${years} years ago` : (
                months > 0 ? `${months} months ago` : (
                days > 0 ? `${days} days ago` : (
                hours > 0 ? `${hours} hours ago` : (
                `${minutes} minutes ago`)))
        )
    }

    useEffect(() => {
        interface LayoutProps {
          name?: string;
        }
        if (data === undefined || Object.keys(data).length === 0) {
            setHashtags([]);
            return;
        }
        const hashtagNodes = data.hashtags.map(({name}: LayoutProps, index: number) => {
            return (
              <ListGroup.Item key={index} className={styles.hashtag}>
                  <Badge>
                      {name}
                  </Badge>
              </ListGroup.Item>
            );
        });
        setHashtags(hashtagNodes);
        setAgo(computeAgo(data.message.date));
    }, [data]);

    return (
        <>
        {(data === undefined ? (
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
         ) : (
            <Card.Body className={styles.info}>
                <div className={styles.reactionsBar}>
                    <div>
                        <Reactions data={data}/>
                    </div>
                    <BsBookmark />
                </div>
                <div className={styles.commentsAndLikesBar}>
                    <span className={styles.caption}>
                        <ListGroup horizontal className={styles.hashtagsBar}>
                            {hashtags}
                        </ListGroup>
                        {data.message.caption}
                    </span>
                    <span className={styles.ago}>{ago}</span>
                </div>
            </Card.Body>
          )
        )}
        </>
    )
}
