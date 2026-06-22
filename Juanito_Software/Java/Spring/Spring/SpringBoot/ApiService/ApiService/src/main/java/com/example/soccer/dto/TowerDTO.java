package com.example.soccer.dto;

import java.util.Stack;

public class TowerDTO {
    private Stack<Integer> tower1;
    private Stack<Integer> tower2;
    private Stack<Integer> tower3;

    public TowerDTO(Stack<Integer> tower1, Stack<Integer> tower2, Stack<Integer> tower3) {
        this.tower1 = tower1;
        this.tower2 = tower2;
        this.tower3 = tower3;
    }

    public Stack<Integer> getTower1() {
        return tower1;
    }

    public Stack<Integer> getTower2() {
        return tower2;
    }

    public Stack<Integer> getTower3() {
        return tower3;
    }
}
