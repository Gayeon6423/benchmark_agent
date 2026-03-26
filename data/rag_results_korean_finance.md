# Korean Finance QA Benchmark Datasets

## 1) Candidate Benchmark Datasets

### ₩on
- **Why Useful**: ₩on is the first open leaderboard for evaluating Korean large language models focused on finance. It covers five multiple-choice question-answering (MCQA) categories: finance and accounting, stock price prediction, domestic company analysis, financial markets, and financial agent tasks, along with one open-ended QA task. This dataset is beneficial for training and evaluating models specifically tailored for Korean financial contexts.
- **URL**: [₩on: Establishing Best Practices for Korean Financial NLP](https://arxiv.org/html/2503.17963)

### KRAFT³-QA
- **Why Useful**: KRAFT³-QA is designed for evaluating tool-augmented agents on QA tasks using Korean financial text and tables. It focuses on structured documents, which are common in corporate filings, making it essential for applications requiring comprehensive reasoning across multiple sections of financial reports.
- **URL**: [KRAFT³-QA: Korean financial text-table benchmark](https://journal.kci.go.kr/jksci/archive/articleView?artiId=ART003234176)

### Kakao Bank Benchmark
- **Why Useful**: Kakao Bank has developed a benchmark aimed at enhancing explainable AI and improving accuracy in processing Korea-specific financial language. This benchmark is significant for developing AI models that require transparency and real-time deployment in regulated financial environments.
- **URL**: [Kakao Bank builds benchmark for Korean finance AI](https://www.koreaherald.com/article/10634678)

## 2) Coverage Gaps
- **Limited Open-Ended Questions**: While existing datasets like ₩on include open-ended QA tasks, there may be a lack of diverse and complex scenarios that require nuanced understanding and reasoning.
- **Integration of Multimodal Data**: Current benchmarks primarily focus on text-based data. There is a need for datasets that integrate text with other modalities, such as images or tables, to reflect real-world financial documents more accurately.
- **Domain-Specific Language Variations**: The datasets may not fully capture the variations in financial terminology and language used across different sectors within the Korean finance industry.

## 3) Suggested Custom QA Benchmark Generation Strategy
- **Data Collection from Real-World Financial Reports**: Gather a diverse set of financial documents, including annual reports, earnings calls, and regulatory filings, to create a comprehensive dataset that reflects real-world scenarios.
- **Crowdsourced Question Generation**: Utilize crowdsourcing platforms to generate questions based on the collected documents, ensuring a wide range of question types and complexities.
- **Incorporate Multimodal Elements**: Develop a benchmark that includes both text and structured data (like tables) to evaluate models on their ability to interpret and reason across different formats.
- **Iterative Testing and Feedback**: Implement a feedback loop where models are tested against the generated questions, and the results are used to refine the dataset and improve question quality.

## 4) URL References
- [₩on: Establishing Best Practices for Korean Financial NLP](https://arxiv.org/html/2503.17963)
- [KRAFT³-QA: Korean financial text-table benchmark](https://journal.kci.go.kr/jksci/archive/articleView?artiId=ART003234176)
- [Kakao Bank builds benchmark for Korean finance AI](https://www.koreaherald.com/article/10634678)