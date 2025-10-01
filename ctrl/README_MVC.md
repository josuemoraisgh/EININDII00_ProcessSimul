
# Refatoração para MVC + SRP

Esta pasta `ctrl/` contém a separação em camadas (Model–View–Controller) e responsabilidades únicas:

- `ui_config.py` — somente constantes de UI.
- `buffers.py` — armazenamento de dados de tempo (`t, y, u`).
- `react_adapter.py` — adaptação mínima de `ReactVar` (sinais/leituras/escritas).
- `plotting/toolbar.py` — toolbar do Matplotlib com ações (V/H/Kp/Limpar/Reset).
- `plotting/canvas.py` — todo o canvas (linhas, cursores, Kp, autoscale, overlays).
- `sim/fopdt.py` — simulador FOPDT independente.
- `utils.py` — conversões utilitárias `u<->%`.
- `model.py` — entende `factory/df/storage` e resolve nomes → ReactVars (MODEL).
- `controller.py` — timers, simulação/real-loop, escrita/leitura de RV, autoscale e redraw (CONTROLLER).
- `view.py` — janela Qt, widgets, liga UI ao controller/model, sem lógica de negócio (VIEW).

## Compatibilidade

- `from ctrl.plant_viewer import PlantViewerWindow` continua funcionando.
- `from ctrl.mpl_canvas import MplCanvas, PVToolbar, UIConfig, ReactVarAdapter, DataBuffers` continua válido.

## Como usar

Substitua os antigos arquivos pelo pacote `ctrl/`. Exemplo:

```python
from ctrl.plant_viewer import PlantViewerWindow
# ... instanciar como antes
```

Nada da funcionalidade foi removido: cursores V/H, Kp com auto-place/edição, +A/-A, Real x Simulado, autoscale, persistência de seleção, toolbar e reset.
