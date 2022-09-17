import React, { useEffect, useState, ReactNode } from 'react';

import { ListGroup } from 'react-bootstrap';
import styles from './Reactions.module.scss';


export const Reactions = ({data}: any) => {
    const [reactions, setReactions] = useState<ReactNode[]>([]);

    useEffect(() => {
        interface LayoutProps {
          emoji: string;
          count: number;
        }
        if (data === undefined || Object.keys(data).length === 0) {
            setReactions([]);
            return;
        }
        console.log("reactions", data.reactions);
        const reactionNodes = data.reactions.map((
                {emoji, count}: LayoutProps,
                index: number) => (
          <ListGroup.Item key={index} className={styles.reactionsBar}>
              {emoji}{count}
          </ListGroup.Item>
        ));
        setReactions(reactionNodes);
    }, [data]);

    return (
        <ListGroup horizontal className={styles.reactionsBar}>
            {reactions}
        </ListGroup>
    );
}

