# LLM Threat Modeling Questions

## 1. System Inputs & Entry Points
1. What are all the interfaces through which users can submit prompts to the LLM?
2. Are there any indirect input vectors (file uploads, document processing, etc.)?
3. How is user authentication handled for different input channels?
4. What input validation exists at each entry point?

## 2. Ecosystem Vulnerabilities
1. What third-party components make up the LLM system's ecosystem?
2. How are dependencies and libraries secured and updated?
3. Are there vulnerabilities in the hosting infrastructure?
4. What network attack surfaces exist in the system's ecosystem?

## 3. Model Security
1. Is this a proprietary, open-source, or third-party provided LLM?
2. What known model vulnerabilities or weaknesses exist?
3. Is the model susceptible to adversarial attacks or jailbreaking techniques?
4. How is the model protected against inference manipulation?

## 4. Prompt Engineering Security
1. How are system prompts and instructions secured?
2. What measures prevent prompt injection attacks?
3. Are there filtering mechanisms for malicious instruction attempts?
4. Could prompt leakage expose sensitive system configurations?

## 5. Data Security
1. What sensitive data might be processed by the LLM?
2. How is training, fine-tuning, and user data secured?
3. Are vector databases or embeddings protected against leakage?
4. What data retention and deletion policies are in place?

## 6. Application Security
1. How is the application layer (frontend, API) secured?
2. What authentication and authorization controls exist?
3. Are there rate limits and abuse prevention mechanisms?
4. How is the application monitored for unusual behavior?

## 7. Pivoting Potential
1. Could the LLM be used to pivot to other systems?
2. What lateral movement paths exist if one component is compromised?
3. Does the LLM have access or connections to sensitive internal systems?
4. What is the blast radius if a compromise occurs?

## 8. Monitoring & Response
1. How are attacks against each vector detected and alerted?
2. Is there a specific incident response plan for LLM-related security events?
3. How are security logs collected and analyzed?
4. What is the process for addressing new attack techniques?
