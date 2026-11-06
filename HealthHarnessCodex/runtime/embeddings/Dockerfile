FROM nvidia/cuda:12.8.1-cudnn-runtime-ubuntu24.04
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false HF_HUB_DISABLE_TELEMETRY=1
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip ca-certificates && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --break-system-packages --no-cache-dir --only-binary=:all: fastembed-gpu==0.9.0 onnxruntime-gpu==1.23.2
COPY worker.py /opt/worker.py
RUN python3 /opt/worker.py --prepare
ENV HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
LABEL com.bigdata.workspace="BigData/HealthHarnessCodex" com.bigdata.component="local-embeddings"
ENTRYPOINT ["python3", "/opt/worker.py"]
