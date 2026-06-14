# AI Paper Reading List

Total papers: 29

## High Priority

### AI Agents

#### EpiBench: Verifiable Evaluation of AI Agents on Epigenomics Analysis

- Score: 20
- Citations: -
- Published: 2026-06-11
- Authors: Harihara Muralidharan, Reema Baskar, Soo Hee Lee, Tim Proctor, Kenny Workman
- Why read it: Matches AI, agents, benchmark, evaluation.
- Matched keywords: AI, agents, benchmark, evaluation, agent, recent
- Abstract: We introduce EpiBench, a verifiable benchmark for short-horizon epigenomics analysis. EpiBench evaluates whether agents can make well-defined analysis decisions from realistic workflow states and return deterministically gradable answers. The benchmark includes 106 evaluations across CUT\&Tag/CUT\&RUN, ATAC-seq, ChIP-seq, and DNA methylation workflows. Across 5,088 valid trajectories from 16 model-harness pairs, no system passed a majority of attempts: GPT-5.5 / Pi led at 45.0\% (143/318 atte...
- Local PDF: papers/ai_agents/2606.13602_EpiBench_Verifiable_Evaluation_of_AI_Agents_on_Epigenomics_Analysis.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.13602v1

#### Benchmarking AI Agents for Addressing Scientific Challenges Across Scales

- Score: 17
- Citations: -
- Published: 2026-06-10
- Authors: Tianyu Liu, Allen Xin Wang, Antonia Panescu, Lisa Xinyi Chen, Wenxin Long, Xinyu Wei, Yueqian Jing, Ziyao Zeng, Jihang Chen, Sihan Jiang, Ziqing Wang, Siyi Gu, Siyu Chen, Xinyang Hu, Haoran Shao, Leqi Xu, Wangjie Zheng, Zhiyuan Cao, Ada Fang, Botao Yu, Kunyang Sun, Rex Ying, Arman Cohan, Qingyu Chen, Lingzhou Xue, Kaize Ding, Yuanqi Du, Wengong Jin, Zhuoran Yang, Marinka Zitnik, James Zou, Hua Xu, Hongyu Zhao
- Why read it: Matches agent, benchmark, evaluation, reasoning.
- Matched keywords: agent, benchmark, evaluation, reasoning, recent
- Abstract: AI agents are increasingly being developed to accelerate scientific discovery, yet their practical capabilities in real research settings remain poorly understood. Existing benchmarks for AI agents rarely capture the complexity, heterogeneity, and extended reasoning required by scientific work, whereas benchmarks for scientific tasks often reduce research to static, direct problems and provide limited support for interactive evaluation. Here, we introduce SciAgentArena, a systematic benchmark...
- Local PDF: papers/ai_agents/2606.12736_Benchmarking_AI_Agents_for_Addressing_Scientific_Challenges_Across_Scales.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.12736v1

#### A Five-Plane Reference Architecture for Runtime Governance of Production AI Agents

- Score: 16
- Citations: 0
- Published: 2026-06-10
- Authors: Krti Tallam
- Why read it: Matches agent, benchmark, evaluation, reasoning.
- Matched keywords: agent, benchmark, evaluation, reasoning, recent
- Abstract: Enterprise security was built to govern data boundaries: the protected surface was data at rest and in transit, and the controls -- access control, data-loss prevention, perimeter inspection -- governed crossings of that boundary. Production AI agents dissolve this assumption. An agent reads context, calls tools, invokes connectors, and modifies systems of record on an enterprise's behalf, so risk moves inside the workflow, into sequences of individually-permitted actions that may transform a...
- Local PDF: papers/ai_agents/2606.12320_A_Five-Plane_Reference_Architecture_for_Runtime_Governance_of_Production_AI_Agents.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.12320v1
- OpenAlex: https://openalex.org/W7164326021

#### Strategic Decision Support for AI Agents

- Score: 15
- Citations: -
- Published: 2026-06-10
- Authors: Shayan Kiyani, Sima Noorani, George Pappas, Hamed Hassani
- Why read it: Matches agent, tool use, recent.
- Matched keywords: agent, tool use, recent
- Abstract: Traditionally, decision support studies how humans use machine learning models to make better decisions. In modern agentic systems, this division of roles is increasingly reversed: AI agents act on behalf of users, while humans and tools becomes support mechanisms around them. This role reversal brings reliability concerns to the forefront, since agentic errors can be consequential and agent behavior must remain aligned with human goals and constraints. Departing from the classical view of de...
- Local PDF: papers/ai_agents/2606.12587_Strategic_Decision_Support_for_AI_Agents.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.12587v1

#### The Internet of Agentic AI: Communication, Coordination, and Collective Intelligence at Scale

- Score: 15
- Citations: -
- Published: 2026-06-11
- Authors: Quanyan Zhu
- Why read it: Matches AI, agents, agent, reasoning.
- Matched keywords: AI, agents, agent, reasoning, recent
- Abstract: The rapid emergence of autonomous AI agents is transforming artificial intelligence from isolated model inference into distributed systems of reasoning, communication, and action. This paper develops the vision of the Internet of Agentic AI (IoAI): an open ecosystem in which heterogeneous agents discover one another, negotiate responsibilities, exchange context, invoke tools, and execute workflows across cloud, edge, device, organizational, and cyber-physical environments. We synthesize found...
- Local PDF: papers/ai_agents/2606.12835_The_Internet_of_Agentic_AI_Communication_Coordination_and_Collective_Intelligence_at_Scale.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.12835v1

#### GeoNatureAgent Benchmark: Benchmarking LLM Agents for Environmental Geospatial Analysis Across Frontier and Open-Weight Foundation Models

- Score: 15
- Citations: -
- Published: 2026-06-11
- Authors: Gabriel Diaz-Ireland, Diego Prieto-Herráez, Mario García Peces, Javier Velázquez, Devika Jain
- Why read it: Matches agent, benchmark, reasoning, recent.
- Matched keywords: agent, benchmark, reasoning, recent
- Abstract: Environmental scientists spend disproportionate effort on data wrangling rather than analysis, and AI agents that automate geospatial workflows remain unvalidated: no benchmark evaluates agents operating through structured tool calling against real APIs. We introduce the GeoNatureAgent Benchmark, the first benchmark for environmental analysis agents that operate via structured tool calls to a production-style geospatial API. It comprises 93 tasks across 18 categories, covering municipality an...
- Local PDF: papers/ai_agents/2606.12821_GeoNatureAgent_Benchmark_Benchmarking_LLM_Agents_for_Environmental_Geospatial_Analysis_Across_Frontier_and_Open-Weight_Foundation.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.12821v1

#### Understanding the Rejection of Fixes Generated by Agentic Pull Requests -- Insights from the AIDev Dataset

- Score: 13
- Citations: 0
- Published: 2026-06-11
- Authors: Mahmoud Abujadallah, Ali Arabat, Mohammed Sayagh
- Why read it: Matches AI, agents, agent, recent.
- Matched keywords: AI, agents, agent, recent
- Abstract: AI coding agents are increasingly used to generate pull requests (PRs) that propose code fixes in software projects. From a first exploration of the AIDev dataset, we find that 46.41\% of the fixes proposed by the agents Copilot, Devin, Cursor, and Claude are rejected. This represents a significant amount of wasted resources that require human reviews, verifications, and running tests and validations for fixes that are merely discarded. Our goal in this paper is to understand the failure mode...
- Local PDF: papers/ai_agents/2606.13468_Understanding_the_Rejection_of_Fixes_Generated_by_Agentic_Pull_Requests_--_Insights_from_the_AIDev_Dataset.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.13468v1
- OpenAlex: https://openalex.org/W7125530472

#### Toward Instructions-as-Code: Understanding the Impact of Instruction Files on Agentic Pull Requests

- Score: 11
- Citations: -
- Published: 2026-06-11
- Authors: Ali Arabat, Mohammed Sayagh
- Why read it: Matches AI, agents, agent, recent.
- Matched keywords: AI, agents, agent, recent
- Abstract: AI-agents (e.g., GitHub Copilot) collaborate as teammates in different software engineering tasks, including code generation proposed through pull requests (Agentic-PRs). For better agent efficiency, developers create instruction files that guide the AI-agents, including how to navigate the project, locate the right components, run tests, respect best practices, and more. In this paper, we investigate the relationship between the creation of these instructions and the performance of AI-agents...
- Local PDF: papers/ai_agents/2606.13449_Toward_Instructions-as-Code_Understanding_the_Impact_of_Instruction_Files_on_Agentic_Pull_Requests.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.13449v1

#### Can I Buy Your KV Cache?

- Score: 10
- Citations: -
- Published: 2026-06-11
- Authors: Luoyuan Zhang
- Why read it: Matches AI, agents, agent, recent.
- Matched keywords: AI, agents, agent, recent
- Abstract: Right now, across the world, AI agents are repeating the same absurd act: to read one document, they each recompute it from scratch. Every agent re-runs prefill, the most compute-intensive step a large model takes, over identical text, only to rebuild a key-value (KV) cache identical to the one the agent before it just built. The same answer, computed a million times. We make a proposal that is almost offensively simple: compute it once. Let a publisher precompute a document's KV cache, and l...
- Local PDF: papers/ai_agents/2606.13361_Can_I_Buy_Your_KV_Cache.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.13361v1

### Interpretability

#### Inference-Time Safety For Code LLMs Via Retrieval-Augmented Revision

- Score: 14
- Citations: -
- Published: 2026-03-02
- Authors: Manisha Mukherjee, Vincent J. Hellendoorn
- Why read it: Matches interpretability, explanation, benchmark, reasoning.
- Matched keywords: interpretability, explanation, benchmark, reasoning, alignment
- Abstract: Large Language Models (LLMs) are increasingly deployed for code generation in high-stakes software development, yet their limited transparency in security reasoning and brittleness to evolving vulnerability patterns raise critical trustworthiness concerns. Models trained on static datasets cannot readily adapt to newly discovered vulnerabilities or changing security standards without retraining, leading to the repeated generation of unsafe code. We present a principled approach to trustworthy...
- Local PDF: papers/interpretability/2603.01494_Inference-Time_Safety_For_Code_LLMs_Via_Retrieval-Augmented_Revision.pdf
- arXiv PDF: https://arxiv.org/pdf/2603.01494v1

#### Enhancing AI Interpretability and Safety through Localised Architectures

- Score: 12
- Citations: -
- Published: 2026-06-06
- Authors: Ian Seet, Jonas Bozenhard, Simon Ostermann
- Why read it: Matches interpretability, reasoning, recent.
- Matched keywords: interpretability, reasoning, recent
- Abstract: Recent advances in generative AI, especially powerful Large Language Models (LLMs) and Large Reasoning Models (LRMs), raise concerns over the interpretability, safety and sustainability of these large and opaque AI models. The power of such architectures is derived not only from the scalability of deep neural networks, but also massively parallel hardware such as GPU clusters. The diffuse nature of deep neural networks gives them great function-approximation capability when provided with suff...
- Local PDF: papers/interpretability/2606.07998_Enhancing_AI_Interpretability_and_Safety_through_Localised_Architectures.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.07998v2

#### GradCFA: A Hybrid Gradient-Based Counterfactual and Feature Attribution Explanation Algorithm for Local Interpretation of Neural Networks

- Score: 11
- Citations: 4
- Published: 2026-03-16
- Authors: Jacob Sanderson, Hua Mao, Wai Lok Woo
- Why read it: Matches interpretability, explanation, recent.
- Matched keywords: interpretability, explanation, recent
- Abstract: Explainable Artificial Intelligence (XAI) is increasingly essential as AI systems are deployed in critical fields such as healthcare and finance, offering transparency into AI-driven decisions. Two major XAI paradigms, counterfactual explanations (CFX) and feature attribution (FA), serve distinct roles in model interpretability. This study introduces GradCFA, a hybrid framework combining CFX and FA to improve interpretability by explicitly optimizing feasibility, plausibility, and diversity -...
- Local PDF: papers/interpretability/2603.15373_GradCFA_A_Hybrid_Gradient-Based_Counterfactual_and_Feature_Attribution_Explanation_Algorithm_for_Local_Interpretation_of_Neural_N.pdf
- arXiv PDF: https://arxiv.org/pdf/2603.15373v1
- OpenAlex: https://openalex.org/W4408564011

#### SwordBench: Evaluating Orthogonality of Steering Image Representations

- Score: 10
- Citations: 0
- Published: 2026-05-10
- Authors: Vladimir Zaigrajew, Dawid Pludowski, Hubert Baniecki, Przemyslaw Biecek
- Why read it: Matches interpretability, benchmark, evaluation, recent.
- Matched keywords: interpretability, benchmark, evaluation, recent
- Abstract: Steering or intervening on model representations at inference time to correct predictions is essential for AI interpretability and safety, yet existing evaluation protocols are limited to ambiguous language modeling tasks. To address this gap, we introduce SwordBench, a benchmark for steering image representations of vision models across multiple backbones and concept removal tasks. Beyond a unified benchmarking suite, we propose new evaluation notions that uncover the second-order effects of...
- Local PDF: papers/interpretability/2605.16372_SwordBench_Evaluating_Orthogonality_of_Steering_Image_Representations.pdf
- arXiv PDF: https://arxiv.org/pdf/2605.16372v1
- OpenAlex: https://openalex.org/W7161916988

### LLM Evaluation

#### Beyond English benchmarks: clinical llm evaluation in Brazilian Portuguese

- Score: 18
- Citations: 0
- Published: 2026-06-05
- Authors: Giordano de Pinho Souza, Glaucia Melo, Josefino Cabral Melo Lima, Daniel Schneider
- Why read it: Matches LLM, evaluation, benchmark, recent.
- Matched keywords: LLM, evaluation, benchmark, recent
- Abstract: Large Language Models are transforming the support for clinical decision and their application in real scenarios. Yet, most benchmarks are conducted in English, and cross-lingual evaluation is needed to tackle the language gaps in global access. We introduce ClinicalBr, the first bilingual benchmark for clinical decision built from real Brazilian case reports. The corpus contains 2,892 cases drawn from 28 SciELO medical journals, spanning 18 specialties, and is structured as parallel Portugue...
- Local PDF: papers/llm_evaluation/2606.07853_Beyond_English_benchmarks_clinical_llm_evaluation_in_Brazilian_Portuguese.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.07853v1
- OpenAlex: https://openalex.org/W7164234520

#### Measuring Epistemic Resilience of LLMs Under Misleading Medical Context

- Score: 18
- Citations: 0
- Published: 2026-06-10
- Authors: Hongjian Zhou, Xinyu Zou, Jinge Wu, Sean Wu, Junchi Yu, Bradley Max Segal, Tobias Erich Niebuhr, Sara Amro, Michael Petrus, Sheikh Momin, Alexandra M. Cardoso Pinto, Rachel Niesen, Laura Sophie Wegner, Dhruv Darji, Jung Moses Koo, Joshua Fieggen, Kapil Narain, Mingde Zeng, Lei Clifton, Linda Shapiro, Fenglin Liu, David A. Clifton
- Why read it: Matches LLM, evaluation, benchmark, agent.
- Matched keywords: LLM, evaluation, benchmark, agent, reasoning, recent
- Abstract: Large language models (LLMs) now reach expert-level scores on medical licensing exams, encouraging the assumption that high scores imply safe medical judgment while patients increasingly use them for health advice. We show this assumption is fragile: when misleading context is injected into questions that LLMs originally answer correctly, they abandon the correct answer. We call the ability to maintain correct judgment under adversarial context epistemic resilience, and introduce MedMisBench...
- Local PDF: papers/llm_evaluation/2606.12291_Measuring_Epistemic_Resilience_of_LLMs_Under_Misleading_Medical_Context.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.12291v1
- OpenAlex: https://openalex.org/W7164414059

#### Cutting LLM Evaluation Costs with SySRs: A Bandit Algorithm that Provably Exploits Model Similarity

- Score: 17
- Citations: 0
- Published: 2026-06-05
- Authors: Zifan Lyu, Chahine Nejma, Tobias Wegel, Fanny Yang, Florian E. Dorner
- Why read it: Matches LLM, evaluation, benchmark, recent.
- Matched keywords: LLM, evaluation, benchmark, recent
- Abstract: Large Language Models are typically benchmarked by evaluating every model on every test query. For practitioners seeking the best model to deploy, this is often wasteful: if a model clearly performs worse than others, there is no need to precisely estimate its performance. Best-arm identification algorithms can be naturally applied to drastically reduce costs by adaptively allocating evaluation budget. Further, language models often respond similarly to the same prompt-a property previous wor...
- Local PDF: papers/llm_evaluation/2606.07726_Cutting_LLM_Evaluation_Costs_with_SySRs_A_Bandit_Algorithm_that_Provably_Exploits_Model_Similarity.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.07726v1
- OpenAlex: https://openalex.org/W7163998755

#### LLM-Based Visualization Evaluation: How Well Do Literacy-Stratified Personas Approximate Human Judgments?

- Score: 17
- Citations: -
- Published: 2026-06-08
- Authors: Swaroop Panda
- Why read it: Matches LLM, evaluation, benchmark, recent.
- Matched keywords: LLM, evaluation, benchmark, recent
- Abstract: Evaluating data visualizations across diverse user populations continues to pose a significant methodological challenge within visualization research. We propose a theorized evaluation framework, Literacy-Stratified LLM Evaluation (LSLE), which formalizes a two-stage process. The first stage involves constructing visualization literacy personas grounded in established frameworks such as VLAT. The second stage directs large language models to adopt these personas as simulated evaluators of vis...
- Local PDF: papers/llm_evaluation/2606.10095_LLM-Based_Visualization_Evaluation_How_Well_Do_Literacy-Stratified_Personas_Approximate_Human_Judgments.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.10095v1

#### SurgiQ: A Large-Scale Multi-Domain Benchmark for Evaluating Surgical Understanding in Large Language Models

- Score: 15
- Citations: 0
- Published: 2026-06-06
- Authors: Ayah Al-Naji, Edoardo Fazzari, Saif Alkindi, Hamdan Alhadhrami, Preslav Nakov, Cesare Stefanini
- Why read it: Matches LLM, evaluation, benchmark, reasoning.
- Matched keywords: LLM, evaluation, benchmark, reasoning, recent
- Abstract: Reliable evaluation of large language models in surgery remains underdeveloped. Broad medical benchmarks test clinical knowledge, while surgery requires procedural reasoning, management trade-offs, negation handling, and selection among plausible operative decisions. We present SurgiQ, a text-only, source-grounded benchmark of 13,055 four-option multiple-choice questions spanning six surgical domains and four question formats: case-based, reasoning, best-option, and negative. SurgiQ is constr...
- Local PDF: papers/llm_evaluation/2606.08071_SurgiQ_A_Large-Scale_Multi-Domain_Benchmark_for_Evaluating_Surgical_Understanding_in_Large_Language_Models.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.08071v1
- OpenAlex: https://openalex.org/W7164234794

#### RealMath-Eval: Why SOTA Judges Struggle with Real Human Reasoning

- Score: 15
- Citations: 0
- Published: 2026-06-08
- Authors: Yiteng Mao, Kenan Xu, Yijia Lyu, Wenhao Li, Jianlong Chen, Xiangfeng Wang
- Why read it: Matches LLM, evaluation, benchmark, reasoning.
- Matched keywords: LLM, evaluation, benchmark, reasoning, recent
- Abstract: While Large Language Models (LLMs) have achieved near-perfect performance in \emph{solving} high-school mathematics, their ability to \emph{evaluate} the diverse reasoning processes of real human students remains under-examined. To bridge this gap, we introduce \textbf{RealMath-Eval}, a rigorously annotated benchmark of 224 real-world exam responses from high schools. Our initial evaluation reveals that even state-of-the-art LLM judges struggle significantly on this task, exhibiting a high Me...
- Local PDF: papers/llm_evaluation/2606.10254_RealMath-Eval_Why_SOTA_Judges_Struggle_with_Real_Human_Reasoning.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.10254v1
- OpenAlex: https://openalex.org/W7164447312

#### From Uncertain Judgments to Calibrated Rankings: Conformal Elo Estimation for LLM Evaluation

- Score: 15
- Citations: -
- Published: 2026-06-11
- Authors: Bora Kargi, David Salinas
- Why read it: Matches LLM, evaluation, recent.
- Matched keywords: LLM, evaluation, recent
- Abstract: Evaluating new large language models typically requires costly human annotation campaigns at scale. LLM-as-a-judge offers a cheaper alternative, but judge scores carry systematic errors - such as position bias, self-preference, or intransitivity - that can strongly miscalibrate the resulting rankings. We quantify the resulting judge-human disagreement at two complementary levels. At the local level, we estimate per-battle uncertainty from the judge's own score differences by propagating calib...
- Local PDF: papers/llm_evaluation/2606.13221_From_Uncertain_Judgments_to_Calibrated_Rankings_Conformal_Elo_Estimation_for_LLM_Evaluation.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.13221v1

#### Agreement in Representation Space for Open-Ended Self-Consistency

- Score: 12
- Citations: -
- Published: 2026-06-10
- Authors: Paula Ontalvilla, Gorka Azkune, Aitor Ormazabal
- Why read it: Matches LLM, evaluation, reasoning, recent.
- Matched keywords: LLM, evaluation, reasoning, recent
- Abstract: Self-consistency improves LLM reasoning by sampling multiple outputs and selecting the most consistent answer, but existing formulations largely rely on exact matching and therefore remain limited to tasks with categorical outputs. In this work, we study self-consistency in open-ended generation tasks such as code synthesis and text summarization. We hypothesize that consistency can be understood as a geometric property of the generation space, where semantically compatible generations concen...
- Local PDF: papers/llm_evaluation/2606.12003_Agreement_in_Representation_Space_for_Open-Ended_Self-Consistency.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.12003v1

#### Support Vector Rubrics: Closing the Gap Between Self-Generated and Human Rubrics

- Score: 10
- Citations: -
- Published: 2026-06-06
- Authors: Mengyuan Sun, Yu Li, Zhuohao Yu, Shikun Zhang, Wei Ye
- Why read it: Matches LLM, evaluation, recent.
- Matched keywords: LLM, evaluation, recent
- Abstract: Rubric-based evaluation is a promising paradigm for judging large language model (LLM) outputs, yet self-generated rubrics lag human-annotated criteria on hard instances. We argue this discriminative gap reflects an objective mismatch: self-generated rubrics describe good responses, whereas effective criteria must discriminate between close candidates. To close this gap, we introduce SVR (Support Vector Rubrics), a framework that recasts rubric construction as max-margin boundary learning ove...
- Local PDF: papers/llm_evaluation/2606.08077_Support_Vector_Rubrics_Closing_the_Gap_Between_Self-Generated_and_Human_Rubrics.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.08077v1

#### Semantic Grading of Written Answers in Low-Resource Language Bangla Using a Fine-Tuned Lightweight Language Model

- Score: 10
- Citations: 0
- Published: 2026-06-10
- Authors: Meherun Farzana, Aniket Joarder, Mahmudul Hasan, Md. Mosaddek Khan
- Why read it: Matches LLM, evaluation, recent.
- Matched keywords: LLM, evaluation, recent
- Abstract: Bangla is among the world's most widely spoken languages, yet it remains underserved in educational NLP research. In many remote and rural regions, access to qualified subject teachers is limited, and written answers are consequently graded largely by hand, restricting timely and consistent feedback. Automatic assessment is challenging because semantically correct responses can vary substantially in surface form. We present a bilingual (Bangla-English) evaluation system designed for low-resou...
- Local PDF: papers/llm_evaluation/2606.11931_Semantic_Grading_of_Written_Answers_in_Low-Resource_Language_Bangla_Using_a_Fine-Tuned_Lightweight_Language_Model.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.11931v1
- OpenAlex: https://openalex.org/W7164332786

## Medium Priority

### AI Agents

#### The Impossibility of Eliciting Latent Knowledge

- Score: 7
- Citations: -
- Published: 2026-06-10
- Authors: Korbinian Friedl, Francis Rhys Ward, Paul Yushin Rapoport, Tom Everitt, Jonathan Richens
- Why read it: Matches agent, recent.
- Matched keywords: agent, recent
- Abstract: Advanced AI systems have extensive knowledge of their environments; in fact, their knowledge may (far) exceed that of their developers or users. Consequently, a desirable property for an AI system is that it is honest -- that it accurately reports its beliefs about the world. Designing an AI system to be honest may be difficult, especially if we want to ask it questions about latent variables in the environment -- variables which are hidden from the human interacting with it. This gives rise...
- Local PDF: papers/ai_agents/2606.12268_The_Impossibility_of_Eliciting_Latent_Knowledge.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.12268v1

### Interpretability

#### Interpretative Interfaces: Designing for AI-Mediated Reading Practices and the Knowledge Commons

- Score: 9
- Citations: 0
- Published: 2026-03-16
- Authors: Gabrielle Benabdallah
- Why read it: Matches interpretability, explanation, recent.
- Matched keywords: interpretability, explanation, recent
- Abstract: Explainable AI (XAI) interfaces seek to make large language models more transparent, yet explanation alone does not produce understanding. Explaining a system's behavior is not the same as being able to engage with it, to probe and interpret its operations through direct manipulation. This distinction matters for scientific disciplines in particular: scientists who increasingly rely on LLMs for reading, citing, and producing literature reviews have little means of directly engaging with how t...
- Local PDF: papers/interpretability/2603.15863_Interpretative_Interfaces_Designing_for_AI-Mediated_Reading_Practices_and_the_Knowledge_Commons.pdf
- arXiv PDF: https://arxiv.org/pdf/2603.15863v1
- OpenAlex: https://openalex.org/W7139080161

#### Diagnosing Generalization Failures from Representational Geometry Markers

- Score: 8
- Citations: -
- Published: 2026-03-02
- Authors: Chi-Ning Chou, Artem Kirsanov, Yao-Yuan Yang, SueYeon Chung
- Why read it: Matches interpretability, mechanistic.
- Matched keywords: interpretability, mechanistic
- Abstract: Generalization, the ability to perform well beyond the training context, is a hallmark of biological and artificial intelligence, yet anticipating unseen failures remains a central challenge. Conventional approaches often take a ``bottom-up'' mechanistic route by reverse-engineering interpretable features or circuits to build explanatory models. While insightful, these methods often struggle to provide the high-level, predictive signals for anticipating failure in real-world deployment. Here,...
- Local PDF: papers/interpretability/2603.01879_Diagnosing_Generalization_Failures_from_Representational_Geometry_Markers.pdf
- arXiv PDF: https://arxiv.org/pdf/2603.01879v1

#### Dual-Modal Lung Cancer AI: Interpretable Radiology and Microscopy with Clinical Risk Integration

- Score: 8
- Citations: -
- Published: 2026-04-17
- Authors: Baramee Sukumal, Aueaphum Aueawatthanaphisut
- Why read it: Matches interpretability, multimodal, recent.
- Matched keywords: interpretability, multimodal, recent
- Abstract: Lung cancer remains one of the leading causes of cancer-related mortality worldwide. Conventional computed tomography (CT) imaging, while essential for detection and staging, has limitations in distinguishing benign from malignant lesions and providing interpretable diagnostic insights. To address this challenge, this study proposes a dual-modal artificial intelligence framework that integrates CT radiology with hematoxylin and eosin (H&E) histopathology for lung cancer diagnosis and subtype...
- Local PDF: papers/interpretability/2604.16104_Dual-Modal_Lung_Cancer_AI_Interpretable_Radiology_and_Microscopy_with_Clinical_Risk_Integration.pdf
- arXiv PDF: https://arxiv.org/pdf/2604.16104v1

#### Model Medicine: A Clinical Framework for Understanding, Diagnosing, and Treating AI Models

- Score: 7
- Citations: -
- Published: 2026-03-05
- Authors: Jihoon Jeong
- Why read it: Matches interpretability, agent.
- Matched keywords: interpretability, agent
- Abstract: Model Medicine is the science of understanding, diagnosing, treating, and preventing disorders in AI models, grounded in the principle that AI models -- like biological organisms -- have internal structures, dynamic processes, heritable traits, observable symptoms, classifiable conditions, and treatable states. This paper introduces Model Medicine as a research program, bridging the gap between current AI interpretability research (anatomical observation) and the systematic clinical practice...
- Local PDF: papers/interpretability/2603.04722_Model_Medicine_A_Clinical_Framework_for_Understanding_Diagnosing_and_Treating_AI_Models.pdf
- arXiv PDF: https://arxiv.org/pdf/2603.04722v2

### LLM Evaluation

#### The Geography of Algorithmic Judgment: LLM Intermediaries, Place Identity, and Racial Steering in Housing Search

- Score: 7
- Citations: 0
- Published: 2026-06-04
- Authors: Hana Samad, Trung Lam, Christoph Mügge-Durum, Michael Akinwumi
- Why read it: Matches evaluation, recent.
- Matched keywords: evaluation, recent
- Abstract: Large language models (LLMs) are rapidly assuming an intermediary role in housing search through the integration of listing platforms within conversational interfaces, mediating access to information, search, and recommendations within urban settings. We expand on prior work on racial steering in LLMs by conducting a behavioral audit of seven open-weight and closed-source LLMs across four U.S. cities, testing location recommendations across three iterative prompting conditions that progressiv...
- Local PDF: papers/llm_evaluation/2606.06694_The_Geography_of_Algorithmic_Judgment_LLM_Intermediaries_Place_Identity_and_Racial_Steering_in_Housing_Search.pdf
- arXiv PDF: https://arxiv.org/pdf/2606.06694v1
- OpenAlex: https://openalex.org/W7164090284
