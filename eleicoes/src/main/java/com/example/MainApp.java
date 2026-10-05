package com.example;

import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.scene.paint.Color;
import javafx.scene.shape.Rectangle;
import javafx.scene.shape.SVGPath;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.stage.Stage;

import java.util.*;
import java.util.stream.Collectors;

public class MainApp extends Application {

    private GerenciadorEleicao gerenciador = new GerenciadorEleicao();
    private Stage stagePrincipal;
    private SessaoEleitoral sessaoAtual;

    private Map<String, SVGPath> mapaSvgEstados = new HashMap<>();
    private Set<String> estadosApurados = new HashSet<>();

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage stage) {
        this.stagePrincipal = stage;
        stage.setTitle("Sistema Eleitoral - Urna Eletrônica & Apuração");
        exibirTelaCadastro();
        stage.show();
    }

    // --- TELA 1: CADASTRO DE CANDIDATOS ---
    private void exibirTelaCadastro() {
        VBox layout = new VBox(12);
        layout.setPadding(new Insets(20));
        layout.setAlignment(Pos.CENTER);

        Label titulo = new Label("Cadastro de Candidatos a Presidente");
        titulo.setFont(Font.font("System", FontWeight.BOLD, 18));

        TextField txtNome = new TextField();
        txtNome.setPromptText("Nome do Candidato");

        TextField txtNumero = new TextField();
        txtNumero.setPromptText("Número (ex: 13, 22)");

        ColorPicker colorPicker = new ColorPicker(Color.BLUE);

        Button btnCadastrar = new Button("Adicionar Candidato");
        ListView<String> listaView = new ListView<>();

        btnCadastrar.setOnAction(e -> {
            if (!txtNome.getText().isEmpty() && !txtNumero.getText().isEmpty()) {
                Candidato c = new Candidato(txtNumero.getText(), txtNome.getText(), colorPicker.getValue());
                gerenciador.adicionarCandidato(c);
                listaView.getItems().add(c.toString());
                txtNome.clear();
                txtNumero.clear();
            }
        });

        Button btnIniciarEleicao = new Button("Iniciar Votação por Estados ->");
        btnIniciarEleicao.setStyle("-fx-background-color: #2e7d32; -fx-text-fill: white; -fx-font-weight: bold; -fx-font-size: 14px;");
        btnIniciarEleicao.setOnAction(e -> {
            if (!gerenciador.getCandidatos().isEmpty()) {
                exibirTelaSelecaoUF();
            } else {
                Alert alert = new Alert(Alert.AlertType.WARNING, "Cadastre pelo menos um candidato!");
                alert.show();
            }
        });

        layout.getChildren().addAll(titulo, txtNome, txtNumero, new Label("Cor no Mapa:"), colorPicker, btnCadastrar, new Label("Candidatos Cadastrados:"), listaView, btnIniciarEleicao);
        stagePrincipal.setScene(new Scene(layout, 450, 580));
    }

    // --- TELA 2: SELEÇÃO DE UF / INICIAR URNA ---
    private void exibirTelaSelecaoUF() {
        VBox layout = new VBox(15);
        layout.setPadding(new Insets(20));
        layout.setAlignment(Pos.CENTER);

        Label titulo = new Label("Sessões Eleitorais por Estado");
        titulo.setFont(Font.font("System", FontWeight.BOLD, 16));

        ComboBox<String> comboUF = new ComboBox<>();
        comboUF.getItems().addAll("AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO");
        comboUF.setValue("PB");

        Button btnIniciarUrna = new Button("Abrir Urna para Votação na UF");
        btnIniciarUrna.setStyle("-fx-font-size: 13px;");
        btnIniciarUrna.setOnAction(e -> {
            sessaoAtual = new SessaoEleitoral(comboUF.getValue());
            exibirTelaUrna();
        });

        Button btnApuracao = new Button("📊 Abrir Painel de Apuração em Tempo Real");
        btnApuracao.setStyle("-fx-background-color: #1565c0; -fx-text-fill: white; -fx-font-weight: bold; -fx-font-size: 13px;");
        btnApuracao.setOnAction(e -> exibirTelaApuracaoEtapas());

        layout.getChildren().addAll(titulo, new Label("Selecione o Estado para Abrir Urna:"), comboUF, btnIniciarUrna, new Separator(), btnApuracao);
        stagePrincipal.setScene(new Scene(layout, 420, 350));
    }

    // --- TELA 3: URNA ELETRÔNICA ---
    private void exibirTelaUrna() {
        HBox root = new HBox(20);
        root.setPadding(new Insets(20));
        root.setStyle("-fx-background-color: #dcdcdc;");

        VBox ecra = new VBox(10);
        ecra.setPrefSize(300, 300);
        ecra.setStyle("-fx-background-color: #ffffff; -fx-border-color: #888888; -fx-padding: 15;");

        Label lblCargo = new Label("PRESIDENTE - UF: " + sessaoAtual.getUf());
        lblCargo.setFont(Font.font("System", FontWeight.BOLD, 14));
        Label lblDisplayNumero = new Label("_ _");
        lblDisplayNumero.setFont(Font.font("System", FontWeight.BOLD, 28));
        Label lblNomeCandidato = new Label("");
        lblNomeCandidato.setFont(Font.font("System", FontWeight.BOLD, 16));

        ecra.getChildren().addAll(lblCargo, new Label("Número:"), lblDisplayNumero, lblNomeCandidato);

        VBox teclado = new VBox(10);
        teclado.setStyle("-fx-background-color: #222222; -fx-padding: 15;");
        teclado.setAlignment(Pos.CENTER);

        GridPane numPad = new GridPane();
        numPad.setHgap(10);
        numPad.setVgap(10);

        StringBuilder digitos = new StringBuilder();

        Runnable atualizarEcra = () -> {
            lblDisplayNumero.setText(digitos.toString());
            Candidato c = gerenciador.buscarPorNumero(digitos.toString());
            if (c != null) {
                lblNomeCandidato.setText("Nome: " + c.getNome());
            } else {
                lblNomeCandidato.setText(digitos.length() >= 2 ? "VOTO NULO" : "");
            }
        };

        int btnIndex = 1;
        for (int r = 0; r < 3; r++) {
            for (int c = 0; c < 3; c++) {
                String val = String.valueOf(btnIndex++);
                Button b = new Button(val);
                b.setPrefSize(45, 45);
                b.setOnAction(e -> {
                    if (digitos.length() < 2) {
                        digitos.append(val);
                        atualizarEcra.run();
                    }
                });
                numPad.add(b, c, r);
            }
        }
        Button b0 = new Button("0");
        b0.setPrefSize(45, 45);
        b0.setOnAction(e -> {
            if (digitos.length() < 2) {
                digitos.append("0");
                atualizarEcra.run();
            }
        });
        numPad.add(b0, 1, 3);

        HBox botoesAcao = new HBox(10);
        Button btnBranco = new Button("BRANCO");
        Button btnCorrige = new Button("CORRIGE");
        Button btnConfirma = new Button("CONFIRMA");

        btnCorrige.setStyle("-fx-background-color: #d32f2f; -fx-text-fill: white;");
        btnConfirma.setStyle("-fx-background-color: #388e3c; -fx-text-fill: white;");

        btnCorrige.setOnAction(e -> {
            digitos.setLength(0);
            atualizarEcra.run();
        });

        btnConfirma.setOnAction(e -> {
            Candidato c = gerenciador.buscarPorNumero(digitos.toString());
            if (c != null) {
                sessaoAtual.registrarVoto(c);
            }
            digitos.setLength(0);
            atualizarEcra.run();
            Alert alert = new Alert(Alert.AlertType.INFORMATION, "Voto Registrado!");
            alert.setHeaderText(null);
            alert.showAndWait();
        });

        botoesAcao.getChildren().addAll(btnBranco, btnCorrige, btnConfirma);

        Button btnEncerrarSessao = new Button("Finalizar Votação em " + sessaoAtual.getUf());
        btnEncerrarSessao.setStyle("-fx-background-color: #f57c00; -fx-text-fill: white; -fx-font-weight: bold;");
        btnEncerrarSessao.setOnAction(e -> {
            gerenciador.salvarSessao(sessaoAtual);
            exibirTelaSelecaoUF();
        });

        teclado.getChildren().addAll(numPad, botoesAcao, new Separator(), btnEncerrarSessao);
        root.getChildren().addAll(ecra, teclado);

        stagePrincipal.setScene(new Scene(root, 650, 420));
    }

    // --- TELA 4: APURAÇÃO POR ETAPAS + MAPA + RANKING ---
    private void exibirTelaApuracaoEtapas() {
        BorderPane root = new BorderPane();
        root.setPadding(new Insets(15));

        VBox topo = new VBox(10);
        topo.setAlignment(Pos.CENTER);

        Label lblTitulo = new Label("APURAÇÃO DAS ELEIÇÕES PRESIDENCIAIS");
        lblTitulo.setFont(Font.font("System", FontWeight.BOLD, 18));

        ProgressBar progressBar = new ProgressBar(0.0);
        progressBar.setPrefWidth(400);

        Label lblStatusApuracao = new Label("Urnas Apuradas: 0.0%");
        lblStatusApuracao.setFont(Font.font("System", FontWeight.BOLD, 13));

        HBox seletorEtapa = new HBox(10);
        seletorEtapa.setAlignment(Pos.CENTER);

        ComboBox<String> comboEstadosDisponiveis = new ComboBox<>();
        List<String> estadosParaApurar = gerenciador.getSessoesEncerradas().stream()
                .map(SessaoEleitoral::getUf)
                .filter(uf -> !estadosApurados.contains(uf))
                .collect(Collectors.toList());

        comboEstadosDisponiveis.getItems().addAll(estadosParaApurar);
        if (!estadosParaApurar.isEmpty()) comboEstadosDisponiveis.setValue(estadosParaApurar.get(0));

        Button btnApurarEstado = new Button("Apurar Estado Selecionado ➔");
        btnApurarEstado.setStyle("-fx-background-color: #2e7d32; -fx-text-fill: white; -fx-font-weight: bold;");

        seletorEtapa.getChildren().addAll(new Label("Escolher Estado para Apurar:"), comboEstadosDisponiveis, btnApurarEstado);

        topo.getChildren().addAll(lblTitulo, progressBar, lblStatusApuracao, seletorEtapa, new Separator());
        root.setTop(topo);

        VBox painelRanking = new VBox(10);
        painelRanking.setPrefWidth(300);
        painelRanking.setPadding(new Insets(10));
        painelRanking.setStyle("-fx-background-color: #f4f4f4; -fx-border-color: #cccccc;");

        Label lblRankingTitulo = new Label("🏆 RANKING NACIONAL");
        lblRankingTitulo.setFont(Font.font("System", FontWeight.BOLD, 15));
        
        VBox listaRanking = new VBox(8);
        painelRanking.getChildren().addAll(lblRankingTitulo, new Separator(), listaRanking);
        root.setRight(painelRanking);

        Pane mapaContainer = new Pane();
        mapaContainer.setPrefSize(450, 450);
        mapaContainer.setStyle("-fx-background-color: #ffffff; -fx-border-color: #dddddd;");
        
        desenharMapaBrasil(mapaContainer);
        root.setCenter(mapaContainer);

        Runnable atualizarTela = () -> {
            int totalSessoesVotadas = gerenciador.getSessoesEncerradas().size();
            int totalApuradas = estadosApurados.size();
            double pct = totalSessoesVotadas > 0 ? (double) totalApuradas / totalSessoesVotadas : 0.0;

            progressBar.setProgress(pct);
            lblStatusApuracao.setText(String.format("Urnas Apuradas: %.1f%% (%d / %d estados)", pct * 100, totalApuradas, totalSessoesVotadas));

            Map<Candidato, Integer> contagemGlobal = new HashMap<>();
            int totalVotosAcumulados = 0;

            for (SessaoEleitoral s : gerenciador.getSessoesEncerradas()) {
                if (estadosApurados.contains(s.getUf())) {
                    for (Map.Entry<Candidato, Integer> entry : s.getVotos().entrySet()) {
                        contagemGlobal.put(entry.getKey(), contagemGlobal.getOrDefault(entry.getKey(), 0) + entry.getValue());
                        totalVotosAcumulados += entry.getValue();
                    }

                    Candidato vencedorUF = s.getVencedor();
                    if (vencedorUF != null && mapaSvgEstados.containsKey(s.getUf())) {
                        mapaSvgEstados.get(s.getUf()).setFill(vencedorUF.getCor());
                    }
                }
            }

            List<Candidato> rankingOrdenado = new ArrayList<>(gerenciador.getCandidatos());
            final int finalTotalVotos = totalVotosAcumulados;
            rankingOrdenado.sort((c1, c2) -> Integer.compare(
                    contagemGlobal.getOrDefault(c2, 0),
                    contagemGlobal.getOrDefault(c1, 0)
            ));

            listaRanking.getChildren().clear();
            int posicao = 1;
            for (Candidato c : rankingOrdenado) {
                int votosC = contagemGlobal.getOrDefault(c, 0);
                double pctC = finalTotalVotos > 0 ? ((double) votosC / finalTotalVotos) * 100 : 0.0;

                HBox item = new HBox(10);
                item.setAlignment(Pos.CENTER_LEFT);
                item.setPadding(new Insets(5));
                item.setStyle("-fx-background-color: #ffffff; -fx-border-color: #e0e0e0; -fx-border-radius: 5;");

                Label lblPos = new Label(posicao + "º");
                lblPos.setFont(Font.font("System", FontWeight.BOLD, 14));

                Rectangle corBox = new Rectangle(15, 15, c.getCor());

                VBox detalhes = new VBox(2);
                Label lblNome = new Label(c.getNome() + " (" + c.getNumero() + ")");
                lblNome.setFont(Font.font("System", FontWeight.BOLD, 12));

                Label lblVotos = new Label(String.format("%d votos (%.1f%%)", votosC, pctC));
                lblVotos.setFont(Font.font("System", 11));

                detalhes.getChildren().addAll(lblNome, lblVotos);
                item.getChildren().addAll(lblPos, corBox, detalhes);

                listaRanking.getChildren().add(item);
                posicao++;
            }

            comboEstadosDisponiveis.getItems().clear();
            List<String> restantes = gerenciador.getSessoesEncerradas().stream()
                    .map(SessaoEleitoral::getUf)
                    .filter(uf -> !estadosApurados.contains(uf))
                    .collect(Collectors.toList());
            comboEstadosDisponiveis.getItems().addAll(restantes);
            if (!restantes.isEmpty()) comboEstadosDisponiveis.setValue(restantes.get(0));
        };

        btnApurarEstado.setOnAction(e -> {
            String ufSelecionada = comboEstadosDisponiveis.getValue();
            if (ufSelecionada != null) {
                estadosApurados.add(ufSelecionada);
                atualizarTela.run();
            }
        });

        Button btnVoltar = new Button("← Voltar para Menu de Sessões");
        btnVoltar.setOnAction(e -> exibirTelaSelecaoUF());
        root.setBottom(new StackPane(btnVoltar));

        atualizarTela.run();
        stagePrincipal.setScene(new Scene(root, 820, 600));
    }

    // --- MAPA DO BRASIL ---
    private void desenharMapaBrasil(Pane container) {
        mapaSvgEstados.clear();

        Map<String, String> pathsUF = new HashMap<>();
        pathsUF.put("RR", "M 130,20 L 170,20 L 160,60 L 120,50 Z");
        pathsUF.put("AP", "M 230,40 L 260,40 L 250,70 L 220,60 Z");
        pathsUF.put("AM", "M 40,60 L 130,60 L 120,130 L 30,110 Z");
        pathsUF.put("PA", "M 160,60 L 240,60 L 230,130 L 140,120 Z");
        pathsUF.put("AC", "M 10,110 L 50,110 L 40,140 L 10,130 Z");
        pathsUF.put("RO", "M 60,120 L 100,120 L 90,160 L 50,150 Z");
        pathsUF.put("MT", "M 110,130 L 180,130 L 170,200 L 100,190 Z");
        pathsUF.put("TO", "M 200,130 L 230,130 L 220,190 L 190,180 Z");
        pathsUF.put("MA", "M 230,80 L 270,80 L 260,130 L 220,120 Z");
        pathsUF.put("PI", "M 260,90 L 285,90 L 280,140 L 255,130 Z");
        pathsUF.put("CE", "M 285,80 L 315,80 L 310,110 L 280,105 Z");
        pathsUF.put("RN", "M 315,85 L 340,85 L 335,100 L 310,100 Z");
        pathsUF.put("PB", "M 315,102 L 345,102 L 340,115 L 310,115 Z");
        pathsUF.put("PE", "M 300,117 L 345,117 L 340,130 L 295,130 Z");
        pathsUF.put("AL", "M 320,132 L 340,132 L 335,142 L 315,142 Z");
        pathsUF.put("SE", "M 315,144 L 332,144 L 328,154 L 310,154 Z");
        pathsUF.put("BA", "M 230,140 L 305,140 L 290,210 L 220,190 Z");
        pathsUF.put("GO", "M 170,190 L 215,190 L 210,240 L 165,230 Z");
        pathsUF.put("DF", "M 195,205 L 205,205 L 205,215 L 195,215 Z");
        pathsUF.put("MS", "M 120,200 L 170,200 L 160,260 L 110,250 Z");
        pathsUF.put("MG", "M 205,210 L 270,210 L 255,260 L 195,250 Z");
        pathsUF.put("ES", "M 270,230 L 285,230 L 280,250 L 265,250 Z");
        pathsUF.put("RJ", "M 245,262 L 275,262 L 270,275 L 240,275 Z");
        pathsUF.put("SP", "M 175,252 L 235,252 L 225,285 L 165,280 Z");
        pathsUF.put("PR", "M 155,282 L 215,282 L 205,310 L 145,305 Z");
        pathsUF.put("SC", "M 160,312 L 210,312 L 202,332 L 152,327 Z");
        pathsUF.put("RS", "M 145,334 L 200,334 L 190,380 L 135,370 Z");

        for (Map.Entry<String, String> entry : pathsUF.entrySet()) {
            String uf = entry.getKey();
            SVGPath statePath = new SVGPath();
            statePath.setContent(entry.getValue());
            statePath.setFill(Color.LIGHTGRAY);
            statePath.setStroke(Color.WHITE);
            statePath.setStrokeWidth(1.5);

            Label lblUf = new Label(uf);
            lblUf.setFont(Font.font("System", FontWeight.BOLD, 9));
            lblUf.setTextFill(Color.DARKSLATEGRAY);

            statePath.boundsInLocalProperty().addListener((obs, oldB, newB) -> {
                lblUf.setLayoutX(newB.getMinX() + (newB.getWidth() / 2) - 8);
                lblUf.setLayoutY(newB.getMinY() + (newB.getHeight() / 2) - 6);
            });

            mapaSvgEstados.put(uf, statePath);
            container.getChildren().addAll(statePath, lblUf);
        }
    }
}