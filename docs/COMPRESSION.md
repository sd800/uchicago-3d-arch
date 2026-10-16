# Web model delivery

The complete web model transfer is **4.85 MB**, compared with the current **37.73 MB** native 3DS. The locally bundled meshoptimizer 1.3.0 codec and gzip restore the exact CAD SHA-256 without quantization or simplification. Compression reduces transfer and duplicate input storage; rendering still uses the full model.

A single worker restores geometry blocks and parses the 3DS; scene creation yields between time slices. The no-worker fallback yields between source objects. Decoder JavaScript/WebAssembly is bundled locally. The root and standalone editions preserve native CAD downloads. See `output/web_model_report.json` for exact byte counts and hashes.

HTTP uses binary assets. Local double-click editions load classic-script assets; standalone HTML embeds its compressed browsing data. Parsing/decompression is cooperative or worker-based where appropriate. Geometry, framebuffers and browser storage remain additional memory costs.
