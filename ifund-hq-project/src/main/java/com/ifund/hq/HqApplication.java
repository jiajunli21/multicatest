package com.ifund.hq;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

@SpringBootApplication
@EnableCaching
public class HqApplication {

    public static void main(String[] args) {
        SpringApplication.run(HqApplication.class, args);
    }
}
