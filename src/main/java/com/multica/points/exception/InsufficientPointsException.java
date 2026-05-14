package com.multica.points.exception;

public class InsufficientPointsException extends PointsException {

    public InsufficientPointsException(String userId) {
        super("INSUFFICIENT_POINTS", "Insufficient balance for user: " + userId);
    }
}
