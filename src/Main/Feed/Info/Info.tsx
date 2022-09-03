import React from 'react';
import { Spinner, Card } from 'react-bootstrap';
import { BsHeart, BsChatRight, BsTelegram, BsBookmark } from 'react-icons/bs';
import { Username } from 'lib/ui/Username/Username';

import styles from './Info.module.scss';

export const Info = ({msg}: any) => {
    return (
        <>
        {(msg === undefined ? (
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
                    <span className={styles.likes}>20 likes</span>
                    <p className={styles.title}>
                        <Username username={msg.user.username} /> {msg.caption}
                    </p>
                    <span className={styles.ago}>19 hours ago</span>
                </div>
            </Card.Body>
          )
        )}
        </>
    )
}
