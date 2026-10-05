package com.example;

import java.util.ArrayList;
import java.util.List;

public class GerenciadorEleicao {
    private List<Candidato> candidatos = new ArrayList<>();
    private List<SessaoEleitoral> sessoesEncerradas = new ArrayList<>();

    public void adicionarCandidato(Candidato c) {
        candidatos.add(c);
    }

    public List<Candidato> getCandidatos() {
        return candidatos;
    }

    public Candidato buscarPorNumero(String numero) {
        for (Candidato c : candidatos) {
            if (c.getNumero().equals(numero)) {
                return c;
            }
        }
        return null;
    }

    public void salvarSessao(SessaoEleitoral sessao) {
        sessoesEncerradas.add(sessao);
    }

    public List<SessaoEleitoral> getSessoesEncerradas() {
        return sessoesEncerradas;
    }
}