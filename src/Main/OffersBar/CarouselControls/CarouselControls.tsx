import React from "react";
import { Container, Row, Col, Button } from "react-bootstrap";


export interface ControlProps {
  onNext: () => void;
  onPrev: () => void;
};

export const CarouselControls = (props: ControlProps) => {
    return (
        <Container>
        <Row className="justify-content-md-center">
            <Col md="auto">
                <Button variant="light" onClick={props.onNext}>{"<<"}</Button>
                <Button variant="light" onClick={props.onPrev}>{">>"}</Button>
            </Col>
        </Row>
        </Container>
    )
};
