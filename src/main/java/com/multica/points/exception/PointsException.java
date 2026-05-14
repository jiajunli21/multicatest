package com.multica.points.exception;

import lombok.Getter;

@Getter
public class PointsException extends RuntimeException {

    private final String errorCode;

    public PointsException(String errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }

    public PointsException(String errorCode, String message, Throwable cause) {
        super(message, cause);
        this.errorCode = errorCode;
    }
}
