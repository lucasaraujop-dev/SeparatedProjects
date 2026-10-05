package com.example;

import java.util.HashMap;
import java.util.Map;

public class SessaoEleitoral {
    private String uf;
    private Map<Candidato, Integer> votos = new HashMap<>();

    public SessaoEleitoral(String uf) {
        this.uf = uf;
    }

    public void registrarVoto(Candidato candidato) {
        votos.put(candidato, votos.getOrDefault(candidato, 0) + 1);
    }

    public String getUf() { return uf; }
    public Map<Candidato, Integer> getVotos() { return votos; }

    public Candidato getVencedor() {
        Candidato vencedor = null;
        int maxVotos = -1;
        for (Map.Entry<Candidato, Integer> entry : votos.entrySet()) {
            if (entry.getValue() > maxVotos) {
                maxVotos = entry.getValue();
                vencedor = entry.getKey();
            }
        }
        return vencedor;
    }
}