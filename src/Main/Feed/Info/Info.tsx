import React, { useEffect, useState, ReactNode } from 'react';
import { Spinner, Card, Badge } from 'react-bootstrap';
import { BsHeart, BsChatRight, BsTelegram, BsBookmark } from 'react-icons/bs';
import { Username } from 'lib/ui/Username/Username';

import styles from './Info.module.scss';

export const Info = ({data}: any) => {
    const [ago, setAgo] = useState<string>("Long time ago...");
    const [badges, setBadges] = useState<ReactNode[]>([]);

    useEffect(() => {
        if (Object.keys(data).length === 0) {
            return;
        }
        console.log(data.message.caption);
    }, [data]);

    useEffect(() => {
        interface LayoutProps {
          name?: string;
        }
        if (Object.keys(data).length === 0) {
            setBadges([]);
            return;
        }
        const hashtagNodes = data.hashtags.map(({name}: LayoutProps) => {
            return (
              <Badge>
                {name}
              </Badge>
            );
        });
        setBadges(hashtagNodes);
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
                        <BsHeart />
                        <BsChatRight />
                        <BsTelegram />
                    </div>
                    <BsBookmark />
                </div>
                <div className={styles.commentsAndLikesBar}>
                    <span className={styles.likes}>
                    "reaction count" reactions
                    </span>
                    <span className={styles.caption}>
                        {badges}
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
