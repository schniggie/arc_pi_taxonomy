# AI generated LLM DevOps Infrastructure Security Assessment Table

| Software | Purpose | Default Port | Web Dashboard Title | Authentication | Notable CVEs |
|----------|---------|--------------|---------------------|----------------|--------------|
| **MLflow** | ML experiment tracking & model registry | 5000 | "MLflow UI" | No (default), Yes (configurable) | CVE-2023-48071, CVE-2023-48070, CVE-2023-1177 (RCE via artifact upload) |
| **Weights & Biases** | ML experiment tracking | 8080 | "Weights & Biases" | Yes (API key) | CVE-2022-31049 (authentication bypass) |
| **Kubeflow** | ML workflows on Kubernetes | 8080 | "Kubeflow" | Yes (OAuth, configurable) | CVE-2023-27484 (SSRF), CVE-2023-4824, CVE-2023-38573 |
| **Kubeflow Pipelines** | ML workflow orchestration | 8080 (Argo UI) | "Argo Workflows" | Yes (K8s RBAC/Dex/OIDC) | CVE-2023-4824, CVE-2023-38573 |
| **KServe (InferenceService)** | Model serving platform | 8080 | "KServe Dashboard" | No (typically) | Relies on K8s security |
| **Ray Dashboard** | Distributed computing framework | 8265 | "Ray Dashboard" | No | CVE-2023-48022 (command injection) |
| **Slurm** | HPC workload manager | 9090 | "Slurm Workload Manager" | Yes (basic auth) | CVE-2023-4915 (privilege escalation) |
| **DVC Studio** | Data/model version control | 8080 | "DVC Studio" | Yes (configurable) | CVE-2022-24439 (path traversal) |
| **Determined AI** | Training platform | 8080 | "Determined AI" | Yes (basic auth) | CVE-2023-25809 (privilege escalation) |
| **Prometheus** | Monitoring | 9090 | "Prometheus Time Series Collection & Processing Server" | No | CVE-2023-46285, CVE-2023-47038, CVE-2021-29622 (open redirect), CVE-2021-36156 (DoS) |
| **Grafana** | Metrics visualization | 3000 | "Grafana" | Yes (built-in) | CVE-2024-28929, CVE-2023-3128 (OAuth account takeover), CVE-2021-43798 (path traversal), CVE-2024-1313 |
| **Jenkins** | CI/CD | 8080 | "Dashboard [Jenkins]" | Yes (form-based) | CVE-2024-23897 (critical file read → RCE), CVE-2023-27898 (SSRF) |
| **GitLab** | Source code management | 80/443 | "GitLab" | Yes (form-based) | CVE-2023-7028 (account takeover), CVE-2023-2825 (RCE), CVE-2022-0154 |
| **Kubernetes Dashboard** | K8s management UI | 8001/443/8443 | "Kubernetes Dashboard" | Yes (token-based) | CVE-2018-18264 (auth bypass), CVE-2020-8554 |
| **Jupyter Hub** | Notebook management | 8000 | "JupyterHub" | Yes (form-based) | CVE-2023-33381 (path traversal) |
| **Docker Registry** | Container registry | 5000 | "Docker Registry" | Optional | CVE-2023-2253 (authentication bypass) |
| **Docker Swarm/UI** | Container orchestration | 8080/443 | "Docker Swarm Visualizer" | No | CVE-2019-16884 (privilege escalation) |
| **Airflow** | Workflow management | 8080 | "Airflow - DAGs" | Yes (configurable) | CVE-2024-31842, CVE-2024-27535, CVE-2023-39508 (code execution), CVE-2020-11978 (RCE) |
