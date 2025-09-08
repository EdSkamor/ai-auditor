# Sprzęt i środowisko

| Komponent            | Wartość                             |
|----------------------|-------------------------------------|
| GPU                  | NVIDIA GeForce **RTX 4090 24 GB**   |
| Sterownik NVIDIA     | 535.x (proprietary)                 |
| CUDA                 | 12.9 + cuBLAS                       |
| CPU / RAM            | $(grep "model name" /proc/cpuinfo | head -1 | cut -d: -f2), $(free -h | awk '/Mem:/ {print $2}') RAM |
| OS                   | Linux Mint 21.3 XFCE                |
| Python               | $(python3 -V) |
| llama.cpp commit     | $(git -C third_party/llama.cpp rev-parse --short HEAD) |

> Do weryfikacji GPU:
> ```bash
> nvidia-smi
> ```
