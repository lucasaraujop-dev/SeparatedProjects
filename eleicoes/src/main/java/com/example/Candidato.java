package com.example;

import javafx.scene.paint.Color;

public class Candidato {
    private String numero;
    private String nome;
    private Color cor;

    public Candidato(String numero, String nome, Color cor) {
        this.numero = numero;
        this.nome = nome;
        this.cor = cor;
    }

    public String getNumero() { return numero; }
    public String getNome() { return nome; }
    public Color getCor() { return cor; }

    @Override
    public String toString() {
        return numero + " - " + nome;
    }
}