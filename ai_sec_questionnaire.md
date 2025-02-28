# AI Security Assessment Questionnaire

## 1. General Information

- **AI System Name:**  
- **Organization/Team Responsible:**  
- **Primary Use Case of AI System:**  
- **Deployment Status:** 
  - [ ] Development  
  - [ ] Testing  
  - [ ] Production  
  - [ ] Decommissioning  

---

## 2. Model Security

1. **What type of AI model is used?** (e.g., LLM, computer vision, reinforcement learning, etc.)  
2. **What system or developer prompt is embedded in the model?**  
3. **Is the model proprietary, open-source, or third-party provided?**  
4. **Does the model include retrieval-augmented generation (RAG)?**  
   - [ ] Yes  
   - [ ] No  
5. **Is the model fine-tuned or zero-shot?**  
6. **Is the AI system multi-modal?**  
   - [ ] Yes  
   - [ ] No  
7. **Is the AI agentic (autonomously taking actions)?**  
   - [ ] Yes  
   - [ ] No  
8. **What tools or APIs does the AI interact with?**  

---

## 3. Storage & Data Security

1. **Where is AI-related data stored?**  
   - [ ] On-premises  
   - [ ] Cloud  
   - [ ] Hybrid  
2. **Which databases are used for model inputs, outputs, or embeddings?**  
3. **Does the system use vector databases for embeddings?**  
   - [ ] Yes  
   - [ ] No  
4. **How is data encrypted at rest and in transit?**  
5. **Are data access controls and audit logs in place?**  
   - [ ] Yes  
   - [ ] No  

---

## 4. Interface Security

1. **What type of interface is used to interact with the AI?**  
   - [ ] Chatbot  
   - [ ] API  
   - [ ] Data upload portal  
   - [ ] Other: _______  
2. **How is input data sanitized to prevent prompt injection?**  
3. **Does the AI system have rate limiting or authentication for external users?**  
   - [ ] Yes  
   - [ ] No  
4. **Is there an approval process for API integrations with external tools?**  
   - [ ] Yes  
   - [ ] No  

---

## 5. Network Architecture & Components

1. **Is the AI system exposed to external networks?**  
   - [ ] Yes  
   - [ ] No  
2. **Does it integrate with external applications?**  
   - [ ] Yes  
   - [ ] No  
   - If yes, which applications? (e.g., Salesforce, Slack, Microsoft Teams, etc.)  
3. **Does it integrate with internal applications?**  
   - [ ] Yes  
   - [ ] No  
   - If yes, does it have read/write permissions?  
     - [ ] Read  
     - [ ] Write  
     - [ ] Both  
4. **Does the AI system use open-source software (OSS)?**  
   - [ ] Yes  
   - [ ] No  
   - If yes, are dependencies monitored for vulnerabilities?  
     - [ ] Yes  
     - [ ] No  
5. **Does the system use internal APIs?**  
   - [ ] Yes  
   - [ ] No  
6. **Does it use a headless browser (e.g., Puppeteer, Selenium)?**  
   - [ ] Yes  
   - [ ] No  
7. **Is there a human-in-the-loop (HITL) component for oversight?**  
   - [ ] Yes  
   - [ ] No  

---

## 6. Development Environment Security

1. **Where is the AI training environment hosted?**  
   - [ ] On-premises  
   - [ ] Cloud  
   - [ ] Hybrid  
2. **What platform is used for prompt engineering and fine-tuning?**  
3. **What development and AI/ML tools are used?** (Select all that apply)  
   - [ ] MLflow  
   - [ ] Kubeflow  
   - [ ] Apache Airflow  
   - [ ] H2O.ai  
   - [ ] TensorFlow  
   - [ ] PyTorch  
   - [ ] AI-as-a-Service (Amazon SageMaker, Azure ML, Google Vertex AI, etc.)  
   - [ ] Other: __________  
4. **How is identity and access management (IAM) handled for developers?**  
5. **Are AI-related workloads isolated from general IT infrastructure?**  
   - [ ] Yes  
   - [ ] No  

---

## 7. AI Supply Chain Security

1. **Does the AI system use third-party AI models or datasets?**  
   - [ ] Yes  
   - [ ] No  
2. **Are security controls in place for model registries?**  
   - [ ] Yes  
   - [ ] No  
3. **Is there a process to detect backdoored or malicious AI models?**  
   - [ ] Yes  
   - [ ] No  
4. **Are virtual machines, containers, and AI platforms hardened against exploits?**  
   - [ ] Yes  
   - [ ] No  
5. **Has the AI system undergone a supply chain security assessment?**  
   - [ ] Yes  
   - [ ] No  
6. **Are Docker images used, and if so, are they verified for security?**  
   - [ ] Yes  
   - [ ] No  

---

## 8. Bias, Safety, and Accuracy

1. **Is bias a concern for this AI system?**  
   - [ ] Yes  
   - [ ] No  
2. **Are fairness and ethical considerations documented?**  
   - [ ] Yes  
   - [ ] No  
3. **Does the AI system make decisions with potential legal or financial impact?**  
   - [ ] Yes  
   - [ ] No  
4. **Has the AI been tested for biases in race, gender, age, or other factors?**  
   - [ ] Yes  
   - [ ] No  
5. **Can the AI system be manipulated into providing unfair advantages (e.g., forced discounts)?**  
   - [ ] Yes  
   - [ ] No  
6. **What safeguards are in place to prevent harmful outputs?**  

---

## 9. Security Testing & Incident Response

1. **Has the AI system undergone security penetration testing?**  
   - [ ] Yes  
   - [ ] No  
2. **Is there an incident response plan specific to AI-related attacks?**  
   - [ ] Yes  
   - [ ] No  
3. **Are AI-generated outputs monitored for anomalies?**  
   - [ ] Yes  
   - [ ] No  
4. **What methods are used to detect adversarial attacks or prompt injection?**  
5. **Are security patches and model updates tracked and applied?**  
   - [ ] Yes  
   - [ ] No  
